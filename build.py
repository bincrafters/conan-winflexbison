#!/usr/bin/env python
# -*- coding: utf-8 -*-


from bincrafters import build_shared, build_template_default

if __name__ == "__main__":

    builder = build_shared.get_builder()

    builder.add(settings={"arch_build": "x86",})
    builder.add(settings={"arch_build": "x86_64",})

    builder.run()
