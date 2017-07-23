import win32con, win32gui, win32api
import threading
import time

def start_monitor_thread(cb):
	wc = win32gui.WNDCLASS()
	wc.hInstance = win32api.GetModuleHandle(None)
	wc.lpszClassName = "TimeChangeMonitor"
	wc.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW;
	wc.hCursor = win32api.LoadCursor( 0, win32con.IDC_ARROW )
	wc.hbrBackground = win32con.COLOR_WINDOW
	wc.lpfnWndProc = {}#wnd_proc # could also specify a wndproc.
	
	try:
		classAtom = win32gui.RegisterClass(wc)
	except win32gui.error as err_info:
		if err_info.winerror != winerror.ERROR_CLASS_ALREADY_EXISTS: raise
	
	thr = threading.Thread(target=monitor_thread, args=(cb,wc), daemon=True)
	thr.start()
	
def monitor_thread(cb, wc):
	hwnd = win32gui.CreateWindow( wc.lpszClassName, "TimeChangeWindow", win32con.WS_OVERLAPPED, 0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT, 0, 0, wc.hInstance, None)
	acc_err = 0
	while True:
		mt, tt = time.monotonic(), time.time()
		win32gui.GetMessage(hwnd, win32con.WM_TIMECHANGE, win32con.WM_TIMECHANGE)
		mtt, ttt = time.monotonic(), time.time()
		x = abs((ttt - tt) - (mtt - mt)) 
		acc_err += x
		if acc_err > 0.1:
			acc_err = 0
			cb()
