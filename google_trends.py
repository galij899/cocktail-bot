from pytrends.request import TrendReq
import matplotlib.pyplot as plt
import io


def generate_plot(data):
    fig, ax = plt.subplots(nrows=1, ncols=1)
    ax.plot(data[data.columns[0]])
    plt.ylabel("Google searches count")
    plt.xlabel("Date")
    plt.title(f"Popularity of {data.columns[0]}")

    buf = io.BytesIO()
    fig.savefig(buf, format='jpg')
    return buf


def get_trends(name):
    pytrends = TrendReq(tz=360)
    kw_list = [name]
    pytrends.build_payload(kw_list, cat=0, timeframe='today 5-y', geo='', gprop='')
    data = pytrends.interest_over_time().drop("isPartial", axis=1)

    line1 = f"People were most interested in {name} at {data[name].idxmax().strftime('%d.%m.%Y')}"
    line2 = f'Today\'s interest in {name} is {"lower" if data[name].mean() <= data[name][-1] else "higher"} than average'
    return generate_plot(data), line1, line2

if __name__ == "__main__":
    print(get_trends())
