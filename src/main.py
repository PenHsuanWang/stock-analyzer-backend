from utils.data_io.data_fetcher import YFinanceFetcher

if __name__ == "__main__":

    data_fetcher = YFinanceFetcher()

    data_fetcher.fetch_from_source(stock_id="TSM", start_date="2020-01-01", end_date="2020-12-31")
    df = data_fetcher.get_as_dataframe()

    print(df.head(10))


