import numpy as np
import sounddevice as sd
from _cffi_backend import _CDataBase
from numpy.typing import NDArray
from queue import Queue
from threading import Thread
from typing import NoReturn

q: Queue[NDArray[np.float32]] = Queue()


def send_input_audio(
    indata: NDArray[np.float32], frames: int, time: _CDataBase, status: sd.CallbackFlags
) -> None:
    if status:
        print(status)
    q.put(indata.copy())
    return


def process_audio(samplerate: int) -> NoReturn:
    while True:
        audio: NDArray[np.float32] = q.get()
        pitch: float = detect_pitch(audio, samplerate)
        print(f"pitch: {pitch:.2f}")


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
    with sd.InputStream(
        samplerate, blocksize, channels=1, callback=send_input_audio, dtype=np.float32
    ):
        Thread(target=process_audio, args=(samplerate,), daemon=True).start()
        input()  # enter to quit.
        return


if __name__ == "__main__":
    main()
