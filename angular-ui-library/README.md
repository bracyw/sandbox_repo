# Angular UI Library MVP

A lightweight Angular UI library MVP inspired by modern React libraries like shadcn/ui, Radix-based patterns, and Tailwind-first design systems.

## What is included

- Tailwind CSS setup for fast utility-first styling
- Reusable primitive components:
  - `UiButtonComponent`
  - `UiCardComponent`
  - `UiInputComponent`
  - `UiBadgeComponent`
- `cn` utility for class merging (`clsx` + `tailwind-merge`)
- Variant-driven API using `class-variance-authority`

## Quick start

```bash
cd angular-ui-library
npm install
npm run build
```

## Library structure

```
projects/ui/src/lib/
  badge/
  button/
  card/
  input/
  utils/
```

## Usage example

```ts
import { UiButtonComponent, UiCardComponent } from '@mvp/ui';
```

Then use in templates:

```html
<ui-card title="Profile" description="Manage your details">
  <ui-input label="Display name" placeholder="Jane Doe" />
  <ui-button variant="default" size="md">Save changes</ui-button>
</ui-card>
```
