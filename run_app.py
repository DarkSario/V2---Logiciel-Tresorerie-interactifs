import logging
import os
import runpy

# Optional dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format='%(asctime)s %(levelname)s %(name)s: %(message)s'
)
logger = logging.getLogger('run_app')

def main():
    try:
        logger.info('Starting application via runpy (module: main)')
        # Run main.py as a module so existing if __name__ guard still applies.
        runpy.run_module('main', run_name='__main__')
    except SystemExit as e:
        logger.info('Process exited with code %s', e.code)
        raise
    except Exception:
        logger.exception('Unhandled exception while running application')
        raise

if __name__ == '__main__':
    main()
