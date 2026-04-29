# Order format
```
{
	"table_id":"1",
	"type":"DINE_IN",
	"status":"PLACED",
	"items":[
		{
		"menu_item_id":"f5",
		"qty":1,
		"unit_price":"90000",
		"status":"QUEUED",
		"station_id":"1",
		"customizations":{
			"0":"a",
			"1":"b"},
		"allergy_notes":""
		}
	],
	"created_at":"2026-04-27T17:58:49.655Z",
	"order_id":0
}
```


# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are is_available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
