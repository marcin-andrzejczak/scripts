import numpy as np
import struct


class WAVError(Exception):
    pass


class WAVFile(object):
    def __init__(self, filename):
        with open(filename, "rb") as f:
            self.chunk_id = f.read(4)
            self.chunk_size, = struct.unpack("<I", f.read(4))
            self.format = f.read(4)

            self.subchunk_1_id = f.read(4)
            (
                self.subchunk_1_size,
                self.audio_format,
                self.num_channels,
                self.sample_rate,
                self.byte_rate,
                self.block_align,
                self.bits_per_sample,
            ) = struct.unpack("<IHHIIHH", f.read(20))
            if self.bits_per_sample != 16:
                raise WAVError("BitsPerSample value not supported!")

            self.subchunk_2_id = f.read(4)
            if self.subchunk_2_id != b"data":
                raise WAVError("Format not supported!")

            self.subchunk_2_size, = struct.unpack("<I", f.read(4))
            self.data = np.fromfile(f, dtype=np.dtype(np.uint16), count=-1)

    def save_to(self, filename):
        with open(filename, "wb") as f:
            f.write(self.chunk_id)
            f.write(struct.pack("<I", self.chunk_size))
            f.write(self.format)

            f.write(self.subchunk_1_id)
            f.write(struct.pack("<IHHIIHH",
                                self.subchunk_1_size,
                                self.audio_format,
                                self.num_channels,
                                self.sample_rate,
                                self.byte_rate,
                                self.block_align,
                                self.bits_per_sample))

            f.write(self.subchunk_2_id)
            f.write(struct.pack("<I", self.subchunk_2_size))
            self.data.tofile(f)

    def __entropy_fast(self, s):
        _, counts = np.unique(s, return_counts=True)
        normed_counts = counts / float(len(s))
        return -np.sum(normed_counts * np.log2(normed_counts))

    def select_entropy(self, required_bits):
        _, start_bit = max(
            (self.__entropy_fast(self.data[sample:sample + required_bits]), sample)
            for sample in range(0, len(self.data) - required_bits, 8)
        )
        return start_bit

    def hide_message(self, message, start):
        self.data.flags.writeable = True

        sample = start
        for character in message:
            character = ord(character)
            for bitcount in range(7, -1, -1):
                self.data[sample] = ((self.data[sample] >> 1) << 1) | (character >> bitcount) & 0x01
                sample += 1

    def read_message(self, start_marker, stop_marker):
        decoded_message = []
        marker = start_marker
        decoding_message = False
        marker_scanner = ""
        char_obtained = 0x00

        for bit, audio_sample in enumerate(self.data, 1):
            char_obtained |= audio_sample & 0x01

            if bit % 8:
                char_obtained <<= 1
            else:
                marker_scanner += chr(char_obtained)
                if marker.startswith(marker_scanner):
                    if len(marker_scanner) == len(marker):
                        if decoding_message:
                            return ''.join(decoded_message)
                        else:
                            decoding_message = True
                            marker_scanner = ""
                            marker = stop_marker
                else:
                    if decoding_message:
                        decoded_message.append(marker_scanner)
                    marker_scanner = ""
                char_obtained = 0x00

    def get_data(self):
        return (self.data, self.sample_rate)
