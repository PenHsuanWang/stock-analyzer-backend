import threading


class CompaniesStore:

    _store = None
    _store_lock = threading.Lock()

    _is_initialized = None

    def __new__(cls, *args, **kwargs):
        with cls._store_lock:
            if cls._store is None:
                cls._store = super().__new__(cls)
                print("create new store instance")
                cls._store._is_initialized = False

            return cls._store

    def __init__(self):

        if not self._is_initialized:
            self._companies = set()

    def add_company_id(self, stock_id):
        self._companies.add(stock_id)

    def remove_company_id(self, stock_id):
        if stock_id in self._companies:
            self._companies.remove(stock_id)

    @property
    def companies_id_store(self):
        return self._companies


def get_store():

    store = CompaniesStore()
    return store


if __name__ == "__main__":

    store = get_store()

    store.add_company_id("AAPL")
    store.add_company_id("GOOG")
    print(store.companies_id_store)
    store.remove_company_id("AAPL")
    print(store.companies_id_store)
