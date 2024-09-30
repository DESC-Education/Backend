import uvicorn
from multiprocessing import cpu_count


def max_workers():
    return cpu_count()


if __name__ == '__main__':
    uvicorn.run('Settings.asgi:application', host='0.0.0.0', port=8000, workers=max_workers(), log_level='info',
                reload=False)
