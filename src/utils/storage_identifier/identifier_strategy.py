
class BaseStorageIdentifierGenerator:
    def generate_identifier(self, *args, **kwargs):
        raise NotImplementedError


class DefaultStockDataIdentifierGenerator(BaseStorageIdentifierGenerator):
    def generate_identifier(self, prefix, stock_id, start_date, end_date):
        identifier = f"{prefix}:{stock_id}:{start_date}:{end_date}"
        return identifier


class SlicingStockDataIdentifierGenerator(BaseStorageIdentifierGenerator):
    def generate_identifier(self, prefix, stock_id, start_date, end_date, post_id=None):
        identifier = f"{prefix}:{stock_id}:{start_date}:{end_date}:{post_id}"
        return identifier


class NullStockDataIdentifierGenerator(BaseStorageIdentifierGenerator):
    def generate_identifier(self, *args, **kwargs):
        identifier = f""
        return identifier
