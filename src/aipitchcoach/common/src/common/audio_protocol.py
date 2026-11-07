import struct
import numpy as np


# ! - BIG ENDIAN
# I - 4 bytes unsigned int (SAMPLE_RATE)
# B - 1 byte unsinged char (CHANNELS)
# B - 1 byte unsigned char (DTYPE_ENUM: 0 = float32 , 1 = int16)

HEADER_FORMAT = "!IBB"
HDEADER_SIZE = struct.calcsize(HEADER_FORMAT)

DTYPE_MAP = {
    0: np.float32,
    1: np.int16
}

DTYPE_REV = {
    np.dtype(np.float32): 0,
    np.dtype(np.int16): 1,
}

def pack_audio(indata, sample_rate, channels) -> bytes:
    """
    Packs the audio data with header into binary blob
    """

    dtype_enum = DTYPE_REV.get(indata.dtype, 1)
    header = struct.pack(HEADER_FORMAT, int(sample_rate), channels, dtype_enum)


    # header + raw audio bytes
    return header + indata.tobytes()


def unpack_audio(binary_packet: bytes):
    """
    Unpacks the binary packet into numpy array
    """

    header = binary_packet[:HDEADER_SIZE]
    sample_rate, channels, dtype_enum = struct.unpack(HEADER_FORMAT, header)

    # converting raw audio bytes into numpy array
    raw_audio = binary_packet[HDEADER_SIZE:]
    target_dtype = DTYPE_MAP.get(dtype_enum)

    audio_np_array = np.frombuffer(raw_audio, dtype=target_dtype)
    audio_np_array = audio_np_array.reshape(-1, channels)

    return sample_rate, channels, audio_np_array