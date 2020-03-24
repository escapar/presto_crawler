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
            'prestospider_detail_page.py',
            '-o',
            'out_detail.json',
        ]
    )
except SystemExit:
    pass