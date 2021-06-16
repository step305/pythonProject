import serial
import time
import UARTParser
import numpy as np
import matplotlib.pyplot as plt


LOG_TIME = 20
SERIAL_DEVICE = 'COM3'

log_code = np.zeros(int(1.5*LOG_TIME*10000), dtype=np.uint8)
log_timit = np.zeros(int(1.5*LOG_TIME*10000), dtype=np.uint16)
log_timms = np.zeros(int(1.5*LOG_TIME*10000), dtype=np.uint32)
log_freq = np.zeros(int(1.5*LOG_TIME*10000), dtype=np.float32)
log_ampl = np.zeros(int(1.5*LOG_TIME*10000), dtype=np.float32)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    port = serial.Serial(port=SERIAL_DEVICE, baudrate=921600,
                         bytesize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE, xonxoff=False,
                         rtscts=False, dsrdtr=False)
    parser_machine = UARTParser.UARTParserState()
    t0 = time.time()
    port.flushInput()
    log_cnt = 0
    while (time.time() - t0) < LOG_TIME:
        data_len = port.in_waiting
        if data_len > 0:
            buffer = port.read(size=data_len)
            # port.flushInput()
            for next_byte in buffer:
                parser_machine.parse_byte(next_byte)
                if parser_machine.data_ready:
                    serial_data = bytes(parser_machine.buffer[0:parser_machine.len])
                    packet = UARTParser.ReportPacketStructure.from_buffer_copy(serial_data)
                    log_timit[log_cnt] = float(packet.timit)
                    log_timms[log_cnt] = float(packet.timms)
                    log_freq[log_cnt] = packet.freq
                    log_ampl[log_cnt] = packet.ampl
                    log_code[log_cnt] = packet.code
                    log_cnt += 1

    plt.figure()
    plt.plot(log_timit[0:log_cnt]/1000.0)
    plt.grid()
    plt.show()

    plt.figure()
    plt.plot(log_timms[0:log_cnt])
    plt.grid()
    plt.show()

    plt.figure()
    plt.plot(log_ampl[0:log_cnt])
    plt.grid()
    plt.show()

    plt.figure()
    plt.plot(log_code[0:log_cnt])
    plt.grid()
    plt.show()

    print('got {} packets'.format(log_cnt))

