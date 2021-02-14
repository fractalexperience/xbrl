from xbrl import pool


class Weaver:
    def __init__(self, data_pool, render_methods):
        self.pool = data_pool
        self.handlers = render_methods

    def invoke(self, name, obj, level):
        render_method = self.handlers.get(name)
        if not render_method:
            return
        render_method(obj, level)

    def loop_base_set(self, bs_key, concept, level):
        if concept is None:
            return
        self.invoke('concept', concept, level)
        cbs_dn = concept.chain_dn.get(bs_key, None)
        if cbs_dn is None:
            return
        for tup in sorted(cbs_dn, key=lambda t: t[1].order):
            cdn = tup[0]
            self.loop_base_set(cdn, bs_key, level+1)

    def loop_base_sets(self):
        for tx in [t[1] for t in self.pool.taxonomies.items()]:
            for bs in tx.base_sets.items():
                self.invoke('base_set', bs, 0)
                for r in bs[1].roots:
                    self.loop_base_set(r, bs[0], 5)