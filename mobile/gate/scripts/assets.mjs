import { fileURLToPath } from "url"
import sharp from "sharp"
import strings from "./strings.js"
import { buildShell } from "../../shared/shell-assets.mjs"

const here = (path) => fileURLToPath(new URL(path, import.meta.url))

await buildShell({ sharp, strings, res: here("../android/app/src/main/res/") })
