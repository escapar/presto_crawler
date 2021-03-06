# from scrapy import cmdline
# cmdline.execute("scrapy runspider prestospider.py".split())



import os
from scrapy.cmdline import execute

os.chdir(os.path.dirname(os.path.realpath(__file__)))

try:
    execute(
        [
            'scrapy',
            'runspider',
            'prestospider.py',
            '-o',
            'out.json',
        ]
    )
except SystemExit:
    pass