from robo_app import application
from sys import platform
import multiprocessing
if __name__ == "__main__":
    if platform == 'darwin':
        multiprocessing.set_start_method("spawn")
    app = application.Application()
    app.mainloop()
