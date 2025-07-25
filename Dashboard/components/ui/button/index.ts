import { cva, type VariantProps } from 'class-variance-authority'

export { default as Button } from './Button.vue'

export const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-all disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg:not([class*=\'size-\'])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive',
  {
    variants: {
      variant: {
        default:
          'bg-orange-600 text-white border border-orange-500 shadow-xs hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-orange-400',
        destructive:
          'bg-orange-800 text-white border border-orange-900 shadow-xs hover:bg-orange-900 focus:outline-none focus:ring-2 focus:ring-orange-400',
        outline:
          'border border-orange-500 bg-transparent text-orange-500 hover:bg-orange-50 hover:text-orange-700 focus:outline-none focus:ring-2 focus:ring-orange-400',
        secondary:
          'bg-orange-100 text-orange-700 border border-orange-300 shadow-xs hover:bg-orange-200 focus:outline-none focus:ring-2 focus:ring-orange-400',
        ghost:
          'bg-transparent text-orange-500 hover:bg-orange-100 hover:text-orange-700 focus:outline-none focus:ring-2 focus:ring-orange-400',
        link:
          'text-orange-600 underline-offset-4 hover:underline hover:text-orange-800 focus:outline-none focus:ring-2 focus:ring-orange-400',
      },
      size: {
        default: 'h-9 px-4 py-2 has-[>svg]:px-3',
        sm: 'h-8 rounded-md gap-1.5 px-3 has-[>svg]:px-2.5',
        lg: 'h-10 rounded-md px-6 has-[>svg]:px-4',
        icon: 'size-9',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)

export type ButtonVariants = VariantProps<typeof buttonVariants>
