import { ChangeDetectionStrategy, Component, HostBinding, Input } from '@angular/core';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../utils/cn';

const badgeVariants = cva(
  'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors',
  {
    variants: {
      variant: {
        default: 'border-transparent bg-primary text-primary-foreground',
        secondary: 'border-transparent bg-secondary text-secondary-foreground',
        outline: 'border-border text-foreground',
        destructive: 'border-transparent bg-destructive text-destructive-foreground'
      }
    },
    defaultVariants: {
      variant: 'default'
    }
  }
);

type BadgeVariants = VariantProps<typeof badgeVariants>;

@Component({
  selector: 'ui-badge',
  standalone: true,
  template: '<ng-content />',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class UiBadgeComponent {
  @Input() variant: BadgeVariants['variant'] = 'default';
  @Input() className = '';

  @HostBinding('class')
  get hostClass(): string {
    return cn(badgeVariants({ variant: this.variant }), this.className);
  }
}
