import os


def feed_dir(output_dir):
    for _ in os.listdir(output_dir):
        p = os.path.join(output_dir, _)
        if os.path.isfile(p):
            fn, ext = os.path.splitext(_)
            date_name = fn.split('_')[1]
            yield p, date_name


def make_output_dirs(output_dir):
    for p, date_name in feed_dir(output_dir):
        target_dir = os.path.join(output_dir, date_name, 'data')
        try:
            os.mkdir(target_dir)
            print('{} is created!'.format(target_dir))
        except FileExistsError as err:
            print(err)
            pass


def mv_files(output_dir):
    for p, date_name in feed_dir(output_dir):
        destination = os.path.join(output_dir, date_name, 'data', 'raw.csv')
        os.rename(p, destination)
        print('{} renamed to {}.'.format(p, destination))


if __name__ == '__main__':
    OUTPUT_DIR = '../output/'
    make_output_dirs(OUTPUT_DIR)
    mv_files(OUTPUT_DIR)
