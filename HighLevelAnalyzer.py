# High Level Analyzer
# For more information and documentation, please go to https://support.saleae.com/extensions/high-level-analyzer-extensions

from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, StringSetting, NumberSetting, ChoicesSetting


# High level analyzers must subclass the HighLevelAnalyzer class.
class Hla(HighLevelAnalyzer):
    # controller_type = ChoicesSetting(choices=('Standard/Dualshock', 'Pop\'n', 'IIDX', 'Guitar Hero')) # Not used for now

    result_types = {
        'controller': {
            'format': 'Controller: {{data.button}}'
        },
        'memcard' : {
            'format': 'Memory Card'
        }
    }

    def __init__(self):
        
        self.found_frame = False
        self.frame_start_time = None
        self.frame_end_time = None
        self.frame_length = 0
        self.frame_count = 0
        self.recv_bytes = []
        self.is_digital_mode = True
        self.is_memory_card = False

    def decode(self, frame: AnalyzerFrame):

        if self.found_frame:    # Process message of packet
            if frame.type == 'result':
                if frame.data['mosi'][0] == 0x42:   # Playstation requesting controller info
                    self.frame_length = frame.data['miso'][0] & 0xF
                    if frame.data['miso'][0] & 0xF0 == 0x40:
                        self.is_digital_mode = True
                    elif frame.data['miso'][0] & 0xF0 == 0x70:
                        self.is_digital_mode = False
                    self.frame_count = 0
                elif self.frame_length > 0:
                    if frame.data['miso'][0] == 0x5A:   # Always 0x5A
                        self.frame_count += 1
                    elif self.frame_count > 0:
                        self.recv_bytes.append(frame.data['miso'][0])
                        self.frame_count += 1
                        if self.frame_count > (self.frame_length * 2):  # Lower nibble of second byte indicates number of 16-bit packets
                            self.found_frame = False
                            output = ''
                            if self.is_digital_mode:
                                if self.recv_bytes[0] & (1 << 0) == 0:
                                    output += 'Select '
                                if self.recv_bytes[0] & (1 << 1) == 0:
                                    output += 'L3 '
                                if self.recv_bytes[0] & (1 << 2) == 0:
                                    output += 'R3 '
                                if self.recv_bytes[0] & (1 << 3) == 0:
                                    output += 'Start '
                                if self.recv_bytes[0] & (1 << 4) == 0:
                                    output += 'Up '
                                if self.recv_bytes[0] & (1 << 5) == 0:
                                    output += 'Right '
                                if self.recv_bytes[0] & (1 << 6) == 0:
                                    output += 'Down '
                                if self.recv_bytes[0] & (1 << 7) == 0:
                                    output += 'Left '
                                if self.recv_bytes[1] & (1 << 0) == 0:
                                    output += 'L2 '
                                if self.recv_bytes[1] & (1 << 1) == 0:
                                    output += 'R2 '
                                if self.recv_bytes[1] & (1 << 2) == 0:
                                    output += 'L1 '
                                if self.recv_bytes[1] & (1 << 3) == 0:
                                    output += 'R1 '
                                if self.recv_bytes[1] & (1 << 4) == 0:
                                    output += 'Triangle '
                                if self.recv_bytes[1] & (1 << 5) == 0:
                                    output += 'Circle '
                                if self.recv_bytes[1] & (1 << 6) == 0:
                                    output += 'Cross '
                                if self.recv_bytes[1] & (1 << 7) == 0:
                                    output += 'Square '
                            if output != '':
                                print('Result: ', output)
                            return AnalyzerFrame('controller', self.start_time, frame.end_time, { 
                                'button' : output
                            })
                            
        else:   # Look for the first byte of a packet
            if frame.type == 'result':
                if frame.data['mosi'][0] == 0x01:   # Controller packet
                    self.is_memory_card = False
                    self.found_frame = True
                    self.start_time = frame.start_time
                    self.frame_length = 0
                    self.recv_bytes = []
                elif frame.data['mosi'][0] == 0x81: # Memory card packet
                    self.is_memory_card = True
                    self.frame_length = 0
                    self.recv_bytes = []
                    return AnalyzerFrame('memcard', frame.start_time, frame.end_time)

