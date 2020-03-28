# source: https://stackoverflow.com/a/45846841
def human_format(num):
    num = float(f'{num:.3g}')
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return f"{f'{num:f}'.rstrip('0').rstrip('.')}" \
           f"{['', 'K', 'M', 'B', 'T'][magnitude]}"
