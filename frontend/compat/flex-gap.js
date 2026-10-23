const probe = document.createElement("div")
probe.style.cssText = "display:flex;flex-direction:column;row-gap:1px;position:absolute;visibility:hidden"
probe.appendChild(document.createElement("div"))
probe.appendChild(document.createElement("div"))
document.documentElement.appendChild(probe)
if (probe.scrollHeight !== 1) document.documentElement.classList.add("no-flex-gap")
document.documentElement.removeChild(probe)
