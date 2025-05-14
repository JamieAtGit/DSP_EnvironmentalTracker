// ✅ new - proper plugin wrapper
import tailwindcss from '@tailwindcss/postcss';

export default {
  plugins: [
    tailwindcss(),
    require('autoprefixer'),
  ]
}
