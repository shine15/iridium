import click
import inspect
import importlib
import threading
import itertools
import sys
import time
import pandas as pd
from datetime import datetime
from iridium.data.hdf5 import HDFData
from iridium.utils.cli import TRADING_DATETIME, DATA_FREQUENCY


class Signal:
    go = True


def spin(msg, signal):
    write, flush = sys.stdout.write, sys.stdout.flush
    for char in itertools.cycle('|/-\\'):
        status = char + ' ' + msg
        write(status)
        flush()
        write('\x08' * len(status))
        time.sleep(.1)
        if not signal.go:
            break
    write(' ' * len(status) + '\x08' * len(status))


@click.group()
def cli():
    pass


@click.option(
    '-t',
    '--token',
    type=str,
    help='access token',
)
@click.option(
    '--data-frequency',
    type=DATA_FREQUENCY,
    default='D',
    show_default=True,
    help=
    '''
    Data frequency 
    M - minute, H - hour, D - day, W - week, M - month    
    M1, M2, M4, M5, M10, M15, M30,
    H1, H2, H3, H4, H6, H8, H12,
    D, W, M
    ''',
)
@click.option(
    '-s',
    '--start',
    type=TRADING_DATETIME,
    help='The start date for history data, default timezone UTC',
)
@click.option(
    '-e',
    '--end',
    type=TRADING_DATETIME,
    default=str(datetime.utcnow()),
    help='The end date for history data, default timezone UTC',
)
@click.option(
    '--tz',
    type=str,
    default=None,
    help='The time zone for start & end date',
)
@click.option(
    '--source',
    default='oanda',
    metavar='SOURCE-NAME',
    show_default=True,
    help='data source',
)
@click.option(
    '-i',
    '--instrument',
    multiple=True,
    help='instrument name such as EUR_USD',
)
@click.option(
    '-f',
    '--file',
    default=None,
    type=click.File('r'),
    help='The file is for using other sources. The class inside must extend iridium.data.hdf5.HDFData',
)
@cli.command()
def data(token, data_frequency, start, end, tz, source, instrument, file):
    signal = Signal()
    spinner = threading.Thread(target=spin,
                               args=('Generating simulation data from {}'.format(source), signal))
    spinner.start()

    start_date_time = pd.Timestamp(start, tz=tz).timestamp()
    end_date_time = pd.Timestamp(end, tz=tz).timestamp()
    if file:
        script = file.read()
        namespace = {}
        code = compile(script, '<string>', 'exec')
        exec(code, namespace)
        for obj in namespace.values():
            if inspect.isclass(obj) \
                    and issubclass(obj, HDFData) \
                    and obj.__name__ != 'HDFData':
                h5 = obj(token=token,
                         instruments=instrument,
                         source=source,
                         start=start_date_time,
                         end=end_date_time,
                         data_frequency=data_frequency)
                file_path = h5.create_hdf5_file()
                click.echo('History data was saved in %s successfully' % file_path)
                break
    else:
        module = importlib.import_module('iridium.data.sources')
        is_source_support = False
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and \
                    issubclass(obj, HDFData) and \
                    source.lower() in obj.__name__.lower():
                is_source_support = True
                h5 = obj(token=token,
                         instruments=instrument,
                         source=source,
                         start=start_date_time,
                         end=end_date_time,
                         data_frequency=data_frequency)
                file_path = h5.create_hdf5_file()
                click.echo('History data was saved in %s successfully' % file_path)
                break
        if not is_source_support:
            click.echo('%s Data source is not supported' % source)

    signal.go = False
    spinner.join()


if __name__ == '__main__':
    cli()
