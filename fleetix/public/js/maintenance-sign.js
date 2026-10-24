(function () {
	var box = document.querySelector(".mt-sign")
	if (!box) return
	var pad = box.querySelector("[data-pad]")
	var error = box.querySelector("[data-error]")
	var save = box.querySelector("[data-save]")
	var ctx = pad.getContext("2d")
	var drawing = false
	var drawn = false

	function fit() {
		pad.width = pad.clientWidth
		pad.height = pad.clientHeight
		ctx.lineWidth = 3
		ctx.lineCap = "round"
		ctx.lineJoin = "round"
		ctx.strokeStyle = "#0d1317"
		drawn = false
	}
	function point(event) {
		var rect = pad.getBoundingClientRect()
		var touch = event.touches ? event.touches[0] : event
		return [touch.clientX - rect.left, touch.clientY - rect.top]
	}
	function begin(event) {
		event.preventDefault()
		var at = point(event)
		drawing = true
		ctx.beginPath()
		ctx.moveTo(at[0], at[1])
	}
	function move(event) {
		if (!drawing) return
		event.preventDefault()
		var at = point(event)
		ctx.lineTo(at[0], at[1])
		ctx.stroke()
		drawn = true
		error.textContent = ""
	}
	function end() {
		drawing = false
	}
	function serverMessage(body) {
		try {
			return JSON.parse(JSON.parse(body._server_messages)[0]).message
		} catch (e) {
			return ""
		}
	}
	function send() {
		if (!drawn) {
			error.textContent = box.dataset.empty
			return
		}
		save.disabled = true
		fetch("/api/method/" + box.dataset.method, {
			method: "POST",
			credentials: "same-origin",
			headers: { Accept: "application/json", "Content-Type": "application/json", "X-Frappe-CSRF-Token": box.dataset.csrf },
			body: JSON.stringify({ visit: box.dataset.visit, key: box.dataset.key, signature: pad.toDataURL("image/png") }),
		})
			.then(function (response) {
				return response.json().then(function (body) {
					if (!response.ok) throw new Error(serverMessage(body) || box.dataset.failed)
					box.hidden = true
					document.querySelector("[data-signed]").hidden = false
				})
			})
			.catch(function (e) {
				error.textContent = e.message || box.dataset.failed
				save.disabled = false
			})
	}

	fit()
	pad.addEventListener("mousedown", begin)
	pad.addEventListener("mousemove", move)
	window.addEventListener("mouseup", end)
	pad.addEventListener("touchstart", begin, { passive: false })
	pad.addEventListener("touchmove", move, { passive: false })
	pad.addEventListener("touchend", end)
	box.querySelector("[data-clear]").addEventListener("click", fit)
	save.addEventListener("click", send)
})()
