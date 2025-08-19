import argparse

from universal_recon.plugins import loader


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--plugin', required=True)
    args = ap.parse_args()
    mods = {m.__name__.split('.')[-1]: m for m in loader.load_plugins()}
    mod = mods.get(args.plugin)
    if not mod:
        raise SystemExit(f'Plugin {args.plugin} not found. Available: {list(mods)}')
    P = getattr(mod, [a for a in dir(mod) if a.endswith('Plugin')][0])()
    for rec in P.fetch():
        if P.validate(rec):
            out = P.transform(rec)
            print(out)


if __name__ == '__main__':
    main()
