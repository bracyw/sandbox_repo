import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { NgIf } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { cn } from '../utils/cn';

@Component({
  selector: 'ui-input',
  standalone: true,
  imports: [FormsModule, NgIf],
  template: `
    <label *ngIf="label" class="mb-2 block text-sm font-medium text-foreground">{{ label }}</label>
    <input
      [(ngModel)]="value"
      [type]="type"
      [placeholder]="placeholder"
      [disabled]="disabled"
      [class]="inputClass"
    />
    <p *ngIf="hint" class="mt-1 text-xs text-muted-foreground">{{ hint }}</p>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class UiInputComponent {
  @Input() label?: string;
  @Input() hint?: string;
  @Input() type = 'text';
  @Input() placeholder = '';
  @Input() disabled = false;
  @Input() className = '';

  value = '';

  get inputClass(): string {
    return cn(
      'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
      this.className
    );
  }
}
