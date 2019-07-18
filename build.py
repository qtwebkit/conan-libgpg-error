#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
import platform

from bincrafters import build_template_default

if __name__ == "__main__":

    builder = build_template_default.get_builder(pure_c=True)

    items = []
    for item in builder.items:
        if item.options["libgpg-error:shared"] == True:
            items.append(item)
    builder.items = items

    builder.run()
