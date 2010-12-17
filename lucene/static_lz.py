# copied from http://stackoverflow.com/questions/479218/how-to-compress-small-strings

import zlib
class trained_short_string_compressor(object):
    def __init__(self,
                 training_set, 
                 bits = -zlib.MAX_WBITS,
                 compression = zlib.Z_DEFAULT_COMPRESSION,
                 scheme = zlib.DEFLATED):
        # Use a negative number of bits, so the checksum is not included.
        compressor = zlib.compressobj(compression,scheme,bits)
        decompressor = zlib.decompressobj(bits)
        junk_offset = 0
        for line in training_set:
            junk_offset += len(line)
            # run the training line through the compressor and decompressor
            junk_offset -= len(decompressor.decompress(compressor.compress(line)))

        # use Z_SYNC_FLUSH. A full flush seems to detrain the compressor, and 
        # not flushing wastes space.
        junk_offset -= len(decompressor.decompress(compressor.flush(zlib.Z_SYNC_FLUSH)))

        self.junk_offset = junk_offset
        self.compressor = compressor
        self.decompressor = decompressor

    def compress(self,s):
        compressor = self.compressor.copy()
        return compressor.compress(s)+compressor.flush()

    def decompress(self,s):
        decompressor = self.decompressor.copy()
        return (decompressor.decompress(s)+decompressor.flush())[self.junk_offset:]
