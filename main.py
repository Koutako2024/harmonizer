import numpy as np
import sounddevice as sd
from _cffi_backend import _CDataBase
from numpy.typing import NDArray
from queue import Queue
from threading import Thread
from typing import NoReturn

input_queue: Queue[NDArray[np.float32]] = Queue()
output_queue: Queue[NDArray[np.float32]] = Queue()


def audio_call_back(
    indata: NDArray[np.float32],
    outdata: NDArray[np.float32],
    frames: int,
    time: _CDataBase,
    status: sd.CallbackFlags,
) -> None:
    if status:
        print(status)
    input_queue.put(indata.copy())
    outdata[:] = output_queue.get().copy()
    return


def process_audio(samplerate: int) -> NoReturn:
    before_pitch: float = 400
    phase: float = 0
    while True:
        # input
        input_audio: NDArray[np.float32] = input_queue.get()
        pitch: float = detect_pitch(input_audio, samplerate)
        print(f"pitch: {pitch:.2f}")

        # output
        # pitch = 400  # DEBUG
        # pitch *= 4  # * 2 ** (-4 / 12)
        pitch *= 2 ** (-1 / 3)

        if pitch > 1600:
            pitch = before_pitch
        else:
            before_pitch = pitch
        t: NDArray[np.float64] = np.arange(len(input_audio)) / samplerate
        note: NDArray[np.float64] = np.sin(pitch * t * 2 * np.pi + phase)
        output_audio: NDArray[np.float32] = note.astype(np.float32)[:, np.newaxis]
        output_queue.put(output_audio)

        # update phase
        phase += 2 * np.pi * pitch * len(input_audio) / samplerate
        phase %= 2 * np.pi  # decrease amount


def detect_pitch(audio: NDArray[np.float32], samplerate: int) -> float:
    audio = audio.ravel()
    audio -= audio.mean()
    corr: np.ndarray = np.correlate(audio, audio, mode="full")
    corr = corr[len(corr) // 2 :]  # 正の周波数だけ検出。
    # 最初に増加し始める場所を検出
    d: np.ndarray = np.diff(corr)
    start: np.intp = np.where(d > 0)[0][0]
    peak: np.intp = np.argmax(corr[start:]) + start
    pitch: float = samplerate / int(peak)
    return pitch


def main() -> None:
    samplerate: int = 44100
    blocksize: int = 2048
    with sd.Stream(
        samplerate, blocksize, channels=1, callback=audio_call_back, dtype=np.float32
    ):
        Thread(target=process_audio, args=(samplerate,), daemon=True).start()
        input()  # enter to quit.
        return


if __name__ == "__main__":
    main()
