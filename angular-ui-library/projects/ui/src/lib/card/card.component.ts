import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { NgIf } from '@angular/common';
import { cn } from '../utils/cn';

@Component({
  selector: 'ui-card',
  standalone: true,
  imports: [NgIf],
  template: `
    <div [class]="containerClass">
      <div class="space-y-1.5 p-6" *ngIf="title || description">
        <h3 class="text-2xl font-semibold leading-none tracking-tight" *ngIf="title">{{ title }}</h3>
        <p class="text-sm text-muted-foreground" *ngIf="description">{{ description }}</p>
      </div>
      <div class="p-6 pt-0">
        <ng-content />
      </div>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class UiCardComponent {
  @Input() title?: string;
  @Input() description?: string;
  @Input() className = '';

  get containerClass(): string {
    return cn('rounded-lg border border-border bg-background text-foreground shadow-sm', this.className);
  }
}
