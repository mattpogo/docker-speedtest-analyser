#!/usr/bin/python

# Script originally provided by AlekseyP
# https://www.reddit.com/r/technology/comments/43fi39/i_set_up_my_raspberry_pi_to_automatically_tweet/
# modifications by roest - https://github.com/roest01

import os
import csv
import time
from speedtest import Speedtest

#static values
CSV_FIELDNAMES=["timestamp", "ping", "download", "upload"]
FILEPATH = os.path.dirname(os.path.abspath(__file__)) + '/../data/result.csv'

def do_speed_test():
        servers = []
        threads = None
        try:
                s = Speedtest()
                s.get_servers(servers)
                s.get_best_server()
                s.download(threads=threads)
                s.upload(threads=threads, pre_allocate=False)
                return s.results.dict(), None
        except Exception as e:
                return None, e

def prune_old_results():
        if not os.path.isfile(FILEPATH) or os.stat(FILEPATH).st_size == 0:
                return

        cutoff_timestamp = (time.time() - 90 * 24 * 60 * 60) * 1000
        batch_duration_ms = 7 * 24 * 60 * 60 * 1000
        with open(FILEPATH, "r", newline="") as f:
                rows = csv.DictReader(f)
                first_row = next(rows, None)
                if first_row is None:
                        return

                oldest_timestamp = float(first_row["timestamp"])
                if oldest_timestamp >= cutoff_timestamp:
                        return

                # Remove at most seven days of the oldest stale data per run.
                drop_before_timestamp = min(oldest_timestamp + batch_duration_ms, cutoff_timestamp)
                recent_rows = [
                        row for row in [first_row, *rows]
                        if float(row["timestamp"]) >= drop_before_timestamp
                ]

        with open(FILEPATH, "w", newline="") as f:
                csv_writer = csv.DictWriter(f, delimiter=',', lineterminator='\n', fieldnames=CSV_FIELDNAMES)
                csv_writer.writeheader()
                csv_writer.writerows(recent_rows)

def runSpeedtest():
        # Keep only the most recent 90 days, even if the speed test fails.
        prune_old_results()

        #run speedtest-cli
        print('--- running speedtest ---')

        #execute speedtest
        result, ex = do_speed_test()
        retries = 0
        while not result and retries < 10:
                print(ex)
                time.sleep(60)
                print('retrying...')
                retries += 1
                result, ex = do_speed_test()
        if not result:
                print('Error running SpeedTest:')
                print(ex)

        #collect speedtest data
        ping = min(1001, round(result['ping'], 2))
        download = round(result['download'] / 1000 / 1000, 2)
        upload = round(result['upload'] / 1000 / 1000, 2)
        timestamp = round(time.time() * 1000, 3)

        csv_data_dict = {
                CSV_FIELDNAMES[0]: timestamp,
                CSV_FIELDNAMES[1]: ping,
                CSV_FIELDNAMES[2]: download,
                CSV_FIELDNAMES[3]: upload}

        #write testdata to file
        isFileEmpty = not os.path.isfile(FILEPATH) or os.stat(FILEPATH).st_size == 0

        with open(FILEPATH, "a", newline="") as f:
                csv_writer = csv.DictWriter(f, delimiter=',', lineterminator='\n', fieldnames=CSV_FIELDNAMES)
                if isFileEmpty:
                        csv_writer.writeheader()
                csv_writer.writerow(csv_data_dict)


        #print testdata
        print('--- Result ---')
        print("Timestamp: %s" %(timestamp))
        print("Ping: %d [ms]" %(ping))
        print("Download: %d [Mbit/s]" %(download))
        print("Upload: %d [Mbit/s]" %(upload))

if __name__ == '__main__':
        runSpeedtest()
        print('speedtest complete')
