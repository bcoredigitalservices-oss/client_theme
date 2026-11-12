// B-One login helpers. Authentication stays 100% in Frappe's own login.js.
(function () {
	var root = document.querySelector(".b1");
	if (!root) return;
	var reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
	var small = matchMedia("(max-width: 960px)").matches;
	var card = root.querySelector(".b1-cardcol");
	var held = function () { return document.hidden || (card && (card.matches(":focus-within") || card.matches(":hover"))); };

	document.addEventListener("visibilitychange", function () {
		root.classList.toggle("is-paused", document.hidden);
	});

	// Password toggle: keep state readable by screen readers
	root.addEventListener("click", function (e) {
		var btn = e.target.closest(".toggle-password");
		if (!btn) return;
		setTimeout(function () {
			var input = document.querySelector(btn.getAttribute("toggle"));
			if (!input) return;
			var shown = input.type === "text";
			btn.setAttribute("aria-pressed", shown ? "true" : "false");
			btn.setAttribute("aria-label", shown ? "Hide password" : "Show password");
		}, 0);
	});

	// Headline carousel: 4 messages, pauses while typing, hovering or focusing the hero
	var slides = root.querySelectorAll(".b1-slide"), dots = root.querySelectorAll(".b1-dots button");
	var hero = root.querySelector(".b1-hero"), cur = 0;
	function show(i) {
		cur = (i + slides.length) % slides.length;
		slides.forEach(function (s, k) { s.classList.toggle("is-on", k === cur); s.setAttribute("aria-hidden", k === cur ? "false" : "true"); });
		dots.forEach(function (d, k) { d.setAttribute("aria-current", k === cur ? "true" : "false"); });
	}
	dots.forEach(function (d, k) { d.addEventListener("click", function () { show(k); }); });
	show(0);
	if (!reduce) setInterval(function () { if (!held() && !hero.matches(":hover, :focus-within")) show(cur + 1); }, 4500);

	// Module pills: zoom carousel drifting left to right
	var car = document.getElementById("b1-car"), trk = document.getElementById("b1-trk");
	if (!car || !trk) return;
	if (reduce || small) { car.classList.add("is-static"); return; }
	var items = [].slice.call(trk.children);
	items.forEach(function (li) { var c = li.cloneNode(true); c.setAttribute("aria-hidden", "true"); trk.appendChild(c); });
	var all = [].slice.call(trk.children), W = trk.scrollWidth / 2 + 7, off = 0, last = 0;
	function tick(t) {
		var dt = Math.min(0.05, (t - last) / 1000 || 0); last = t;
		if (!held() && !car.matches(":hover")) off = (off + 44 * dt) % W;
		trk.style.transform = "translate3d(" + (off - W) + "px,0,0)";
		var r = car.getBoundingClientRect(), cx = r.left + r.width / 2;
		for (var i = 0; i < all.length; i++) {
			var q = all[i].getBoundingClientRect(), k = Math.max(0, 1 - Math.abs(q.left + q.width / 2 - cx) / (r.width * 0.42));
			all[i].style.transform = "scale(" + (0.86 + 0.28 * k).toFixed(3) + ")";
			all[i].style.opacity = (0.5 + 0.5 * k).toFixed(2);
		}
		requestAnimationFrame(tick);
	}
	requestAnimationFrame(tick);
})();
