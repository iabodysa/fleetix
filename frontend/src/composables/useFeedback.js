let audio = null

function context() {
	const Context = window.AudioContext || window.webkitAudioContext
	if (!Context) return null
	if (!audio) audio = new Context()
	return audio
}

function tone(frequency, start, length) {
	const ctx = context()
	if (!ctx) return
	const oscillator = ctx.createOscillator()
	const gain = ctx.createGain()
	oscillator.type = "sine"
	oscillator.frequency.value = frequency
	gain.gain.setValueAtTime(0.0001, ctx.currentTime + start)
	gain.gain.exponentialRampToValueAtTime(0.25, ctx.currentTime + start + 0.02)
	gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + start + length)
	oscillator.connect(gain).connect(ctx.destination)
	oscillator.start(ctx.currentTime + start)
	oscillator.stop(ctx.currentTime + start + length)
}

function vibrate(pattern) {
	if (navigator.vibrate) navigator.vibrate(pattern)
}

export function success() {
	try {
		tone(880, 0, 0.12)
		tone(1320, 0.1, 0.18)
	} catch (e) {
		return vibrate(60)
	}
	vibrate(60)
}

export function problem() {
	try {
		tone(220, 0, 0.25)
	} catch (e) {
		return vibrate([80, 60, 80])
	}
	vibrate([80, 60, 80])
}
