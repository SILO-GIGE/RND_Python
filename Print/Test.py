from PIL import Image
from brother_ql.conversion import convert
from brother_ql.backends.helpers import send
from brother_ql.raster import BrotherQLRaster
im = Image.open("C:\\Users\\silolab_ksh\\Desktop\\TDMovieOut.0.bmp")

backend = 'pyusb'    # 'pyusb', 'linux_kernal', 'network'
model = 'QL-700' # your printer model.

printer = 'usb://0x04f9:0x2042/710644601811' # Get these values from the Windows usb driver filter.  Linux/Raspberry Pi uses '/dev/usb/lp0'.

qlr = BrotherQLRaster(model)
qlr.exception_on_warning = True

instructions = convert(

        qlr=qlr,
        images=[im],    #  Takes a list of file names or PIL objects.
        label='62',     # 프린터가 출력 거부하면 해당 모델 가범위 찾을 것.
        rotate='0',    # 'Auto', '0', '90', '270'
        threshold=50,    # Black and white threshold in percent.
        dither=True,    # 흑백 색감 퀄리티 표현
        compress=True,
        red=False,    # Only True if using Red/Black 62 mm label tape.
        dpi_600=False,
        hq=True,    # False for low quality.
        cut=True

)

# 여기까지는 실행 됨. 밑에 send함수에서 문제발생
send(instructions=instructions, printer_identifier=printer, backend_identifier=backend, blocking=True)