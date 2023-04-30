import redis
from django.conf import settings

from shop.models import Product

r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)


class Recommender:
    @staticmethod
    def get_product_key(pk):
        return f'product:{pk}:purchased_with'

    def product_bought(self, products):
        product_pks = [p.pk for p in products]
        for product_pk in product_pks:
            for with_pk in product_pks:
                if product_pk != with_pk:
                    r.zincrby(self.get_product_key(product_pk), 1, with_pk)

    def suggest_products_for(self, products, max_results=6):
        product_pks = [p.pk for p in products]
        if len(products) == 1:
            suggestions = r.zrange(self.get_product_key(product_pks[0]), 0, -1, desc=True)[:max_results]
        else:
            flat_pks = ''.join([str(pk) for pk in product_pks])
            tmp_key = f'tmp_{flat_pks}'
            keys = [self.get_product_key(pk) for pk in product_pks]
            r.zunionstore(tmp_key, keys)
            r.zrem(tmp_key, *product_pks)
            suggestions = r.zrange(tmp_key, 0, -1, desc=True)[:max_results]

        suggested_product_pks = [int(pk) for pk in suggestions]
        suggested_product = list(Product.objects.filter(id__in=suggested_product_pks))
        suggested_product.sort(key=lambda x: suggested_product_pks.index(x.id))
        return suggested_product

    def clear_purchases(self):
        for pk in Product.objects.values_list('id', flat=True):
            r.delete(self.get_product_key(pk))
