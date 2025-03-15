import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	build: {
		assetsInlineLimit: Infinity
	},

	plugins: [sveltekit()]
});