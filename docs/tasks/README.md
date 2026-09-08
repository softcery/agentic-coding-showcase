# Tasks

One YAML file per task. `_example.yaml` gives 11 keys and their order.

Folder = state. Move the file, add no field.

```
backlog/   not scheduled
next/      ready to build
progress/  in build
done/      built and reviewed
```

File name: `<domain>-<number>-<name>.yaml`. Domain matches one document in
`spec/`. Task cite resolves in task references or in that document. Number
orders tasks inside one domain.

## Procedure

1. Copy `_example.yaml` into `backlog/` as `<domain>-00-<name>.yaml`.
2. Fill purpose, scope, design, acceptance, steps, limits.
3. List ids this task waits on in `after`.
4. To schedule, `git mv` into `next/` and set the number.
5. To start, `git mv` into `progress/`.
6. During build, edit this file only.
7. Write each outcome into `results`. Give each number an evidence path.
8. After review, `git mv` into `done/`.
