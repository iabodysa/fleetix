(function () {
	var box = document.querySelector(".mt-sign")
	if (!box) return
	var sheet = box.querySelector("[data-sheet]")
	var pad = box.querySelector("[data-pad]")
	var error = box.querySelector("[data-error]")
	var save = box.querySelector("[data-save]")
	var ctx = pad.getContext("2d")
	var strokes = []
	var current = null
	var size = [0, 0]

	function paint() {
		var ratio = window.devicePixelRatio || 1
		ctx.setTransform(ratio, 0, 0, ratio, 0, 0)
		ctx.clearRect(0, 0, size[0], size[1])
		ctx.lineWidth = 3
		ctx.lineCap = "round"
		ctx.lineJoin = "round"
		ctx.strokeStyle = "#0d1317"
		strokes.forEach(function (line) {
			ctx.beginPath()
			line.forEach(function (at, i) {
				if (i) ctx.lineTo(at[0], at[1])
				else ctx.moveTo(at[0], at[1])
			})
			if (line.length === 1) ctx.lineTo(line[0][0] + 0.1, line[0][1])
			ctx.stroke()
		})
	}
	function fit() {
		var width = pad.clientWidth
		var height = pad.clientHeight
		if (!width || !height) return
		if (size[0] && size[1] && (width !== size[0] || height !== size[1])) {
			var scale = Math.min(width / size[0], height / size[1])
			strokes = strokes.map(function (line) {
				return line.map(function (at) {
					return [at[0] * scale, at[1] * scale]
				})
			})
		}
		var ratio = window.devicePixelRatio || 1
		pad.width = Math.round(width * ratio)
		pad.height = Math.round(height * ratio)
		size = [width, height]
		paint()
	}
	function point(event) {
		var rect = pad.getBoundingClientRect()
		var touch = event.touches ? event.touches[0] : event
		return [touch.clientX - rect.left, touch.clientY - rect.top]
	}
	function begin(event) {
		event.preventDefault()
		current = [point(event)]
		strokes.push(current)
		error.textContent = ""
		paint()
	}
	function move(event) {
		if (!current) return
		event.preventDefault()
		current.push(point(event))
		paint()
	}
	function end() {
		current = null
	}
	function clear() {
		strokes = []
		paint()
	}
	function open() {
		sheet.hidden = false
		document.documentElement.classList.add("mt-sign-lock")
		if (sheet.requestFullscreen) sheet.requestFullscreen().catch(function () {})
		requestAnimationFrame(fit)
	}
	function close() {
		sheet.hidden = true
		document.documentElement.classList.remove("mt-sign-lock")
		if (document.fullscreenElement && document.exitFullscreen) document.exitFullscreen().catch(function () {})
	}
	function serverMessage(body) {
		try {
			return JSON.parse(JSON.parse(body._server_messages)[0]).message
		} catch (e) {
			return ""
		}
	}
	function send() {
		if (!strokes.length) {
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
					close()
					box.hidden = true
					document.querySelector("[data-signed]").hidden = false
				})
			})
			.catch(function (e) {
				error.textContent = e.message || box.dataset.failed
				save.disabled = false
			})
	}

	pad.addEventListener("mousedown", begin)
	pad.addEventListener("mousemove", move)
	window.addEventListener("mouseup", end)
	pad.addEventListener("touchstart", begin, { passive: false })
	pad.addEventListener("touchmove", move, { passive: false })
	pad.addEventListener("touchend", end)
	window.addEventListener("resize", function () {
		if (!sheet.hidden) fit()
	})
	box.querySelector("[data-open]").addEventListener("click", open)
	box.querySelector("[data-close]").addEventListener("click", close)
	box.querySelector("[data-clear]").addEventListener("click", clear)
	save.addEventListener("click", send)
})()
