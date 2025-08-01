import { Config } from "./src/config";

let url = 'https://learn.svelte.dev/';
let match = 'https://learn.svelte.dev/**';
let maxPagesToCrawl = 5000;

export const defaultConfig: Config = {
  url,
  match,
  maxPagesToCrawl,
  outputFileName: 'saved/learn.svelte.dev.json'
};
