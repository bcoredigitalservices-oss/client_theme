// B-One desk branding. Overrides what the desk shows without editing Frappe or ERPNext files.
(function () {
	const IMG = "/assets/client_theme/images";

	// Built-in fallback, used only when B-One Settings has no tiles yet.
	// Same shape as frappe.boot.b1_tiles rows, which the server filters by role.
	const DEFAULT_TILES = [
		{ module: "Accounts", title: "Finance", icon: "finance" },
		{ module: "Selling", title: "Sales", icon: "sales" },
		{ module: "CRM", title: "CRM", icon: "crm" },
		{ module: "Buying", title: "Procurement", icon: "procurement" },
		{ module: "Stock", title: "Inventory", icon: "inventory" },
		{ module: "Manufacturing", title: "Manufacturing", icon: "manufacturing" },
		{ module: "Projects", title: "Projects", icon: "projects" },
		{ module: "Assets", title: "Assets", icon: "assets" },
		{ module: "Quality", title: "Quality", icon: "quality" },
		{ module: "Support", title: "Support", icon: "support" },
	];
	const DEFAULT_ADMIN = { module: "Setup", title: "Settings", icon: "settings" }; // System Managers only

	function shell_key(module) {
		const all = frappe.boot.module_sidebars || {};
		return all[module] ? module : Object.keys(all).find((k) => all[k].module === module);
	}

	function source_tiles() {
		// Configured in Desk > B-One Settings. Defined (even if empty) means "use exactly this".
		if (Array.isArray(frappe.boot.b1_tiles)) return frappe.boot.b1_tiles;
		const list = DEFAULT_TILES.slice();
		if (frappe.user && frappe.user.has_role && frappe.user.has_role("System Manager")) list.push(DEFAULT_ADMIN);
		return list;
	}

	function tiles() {
		const nav = frappe.app && frappe.app.sidebar;
		const out = [];
		source_tiles().forEach((t, i) => {
			let route = t.route || "";
			if (!route) {
				const key = t.module && shell_key(t.module);
				if (!key) return; // module not installed, or this user cannot open it
				route = (nav && nav.module_landing_route(key)) || "/desk";
			}
			const icon = t.icon || "finance";
			out.push({
				app_name: "b-one-" + icon + "-" + i,
				app_title: __(t.title),
				app_route: route,
				desk_route: "",
				module_icons: [],
				dock: [],
				on_apps_screen: true,
				sequence_id: i,
				app_logo_url: t.custom_icon || `${IMG}/modules/${icon}.svg`,
			});
		});
		return out;
	}

	function install() {
		const u = window.frappe && frappe.utils;
		if (!u || !u.get_apps_screen_apps) return false;
		if (u.__b1) return true;
		u.__b1 = true;

		// Apps screen: one tile per configured module instead of the ERPNext and Framework tiles.
		const orig_apps = u.get_apps_screen_apps;
		u.get_apps_screen_apps = function () {
			try {
				const configured = Array.isArray(frappe.boot.b1_tiles);
				const t = tiles();
				if (t.length || configured) return t;
			} catch (e) {
				console.error("B-One tiles failed, using default apps screen", e); // eslint-disable-line no-console
			}
			return orig_apps.apply(this, arguments);
		};

		// The mark at the top of the dock and sidebar header: always B-One.
		// Both variants are rendered; CSS shows the white/cyan one on navy surfaces
		// (dock, dark mode) and the navy one elsewhere, including inside the white circle on the apps screen.
		const orig_logo = u.app_logo;
		if (orig_logo) {
			u.app_logo = function (app) {
				const r = orig_logo.call(this, app);
				if (!r) return r;
				return {
					icon:
						`<img class="b1-mark b1-mark--dark" src="${IMG}/logo-mark-clean.svg" alt="B-One" />` +
						`<img class="b1-mark b1-mark--light" src="${IMG}/logo-mark-clean-light.svg" alt="" aria-hidden="true" />`,
					title: "B-One",
				};
			};
		}
		return true;
	}


	// ---- Brand, About and Support (replace the Frappe About dialog and the "Frappe Support" link) ----
	const BRAND_DEFAULT = {
		name: "B-One", vendor: "B-Core Digital", website: "https://bcore.digital",
		client: "", version: "", support_email: "bcoredigitalservices@gmail.com", support_url: "",
	};
	function brand() {
		return Object.assign({}, BRAND_DEFAULT, (window.frappe && frappe.boot && frappe.boot.b1_brand) || {});
	}
	function esc(v) {
		return frappe.utils.escape_html(String(v == null ? "" : v));
	}

	function show_about() {
		const b = brand();
		if (!frappe.ui.misc.__b1_about) {
			frappe.ui.misc.__b1_about = new frappe.ui.Dialog({
				title: __("About"),
				primary_action_label: __("Copy version details"),
				primary_action() {
					const done = (v) => {
						frappe.utils.copy_to_clipboard(JSON.stringify(v, null, "\t"));
					};
					frappe.call({
						method: "frappe.utils.change_log.get_versions",
						callback: (r) => {
							const out = { [brand().name]: brand().version || "n/a" };
							Object.entries(r.message || {}).forEach(([k, v]) => (out[k] = v.branch_version || v.version));
							done(out);
						},
						error: () => done({ [brand().name]: brand().version || "n/a" }),
					});
				},
			});
		}
		const d = frappe.ui.misc.__b1_about;
		d.$wrapper.addClass("b1-about-dialog"); // the outer .modal (dialog.wrapper is the inner .modal-dialog)
		const rows = [
			[__("Version"), esc(b.version || "-")],
			b.client ? [__("Prepared for"), esc(b.client)] : null,
			[__("Website"), `<a href="${esc(b.website)}" target="_blank" rel="noopener">${esc(b.website.replace(/^https?:\/\//, ""))}</a>`],
			[__("Support"), `<a href="mailto:${esc(b.support_email)}">${esc(b.support_email)}</a>`],
		].filter(Boolean);
		$(d.body).html(
			`<div class="b1-about">
				<img class="b1-about-logo" src="${IMG}/logo-mark-clean.svg" alt="${esc(b.name)}" />
				<div class="b1-about-name">${esc(b.name)}</div>
				<div class="b1-about-by">${__("by")} ${esc(b.vendor)}</div>
				<dl class="b1-about-rows">${rows.map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join("")}</dl>
				<p class="b1-about-legal">${__("&copy; {0} {1}. Includes open-source components used under their respective licences.", [new Date().getFullYear(), esc(b.vendor)])}</p>
			</div>`
		);
		d.show();
	}

	function show_support() {
		const b = brand();
		const info = [
			`Site: ${location.host}`,
			`User: ${frappe.session.user}`,
			`${b.name}: ${b.version || "n/a"}`,
			`Page: ${location.href}`,
		].join("\n");
		const subject = `Support request${b.client ? " - " + b.client : ""}`;
		const body = `Describe the problem:\n\n\n---\n${info}`;
		const mailto = `mailto:${b.support_email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;

		// A Dialog only renders its footer button when primary_action is passed to the constructor
		// (same pattern as the About dialog). The mailto link changes on every open, so it is stored on the dialog.
		if (!frappe.ui.misc.__b1_support) {
			frappe.ui.misc.__b1_support = new frappe.ui.Dialog({
				title: __("Support"),
				primary_action_label: __("Email support"),
				primary_action() {
					window.location.href = frappe.ui.misc.__b1_support.__b1_mailto;
				},
			});
		}
		const d = frappe.ui.misc.__b1_support;
		d.__b1_mailto = mailto;
		$(d.body).html(
			`<div class="b1-support">
				<p>${__("Need help? Our team at {0} will get back to you.", [esc(b.vendor)])}</p>
				<p class="b1-support-mail"><a href="mailto:${esc(b.support_email)}">${esc(b.support_email)}</a>
					<button type="button" class="btn btn-xs b1-copy-email">${__("Copy")}</button></p>
				${b.support_url ? `<p><a href="${esc(b.support_url)}" target="_blank" rel="noopener">${__("Open support portal")}</a></p>` : ""}
				<p class="b1-support-note">${__("The email includes your site, user and version to help us respond faster.")}</p>
			</div>`
		);
		$(d.body).off("click.b1").on("click.b1", ".b1-copy-email", () => frappe.utils.copy_to_clipboard(b.support_email));
		d.show();
	}

	function install_brand_ui() {
		if (!(window.frappe && frappe.ui && frappe.ui.Dropdown && frappe.ui.toolbar && frappe.ui.misc && frappe.ui.Dialog)) return false;
		if (frappe.ui.__b1_brand) return true;
		frappe.ui.__b1_brand = true;

		// "About" opens B-One's own dialog everywhere (avatar menu, awesome bar, help menus).
		frappe.ui.toolbar.show_about = show_about;
		frappe.ui.misc.about = show_about;
		frappe.ui.toolbar.b1_support = show_support;

		// Any dropdown row labelled "Frappe Support" becomes "Support" and opens our dialog.
		const Orig = frappe.ui.Dropdown;
		const fix = (row) => {
			if (row && typeof row.label === "string" && /frappe\s+support/i.test(row.label)) {
				const r = Object.assign({}, row, { label: __("Support"), icon: "life-buoy", onclick: show_support });
				delete r.href;
				delete r.url;
				return r;
			}
			return row;
		};
		class B1Dropdown extends Orig {
			constructor(opts = {}) {
				if (Array.isArray(opts.options)) opts = Object.assign({}, opts, { options: opts.options.map(fix) });
				super(opts);
			}
		}
		frappe.ui.Dropdown = B1Dropdown;
		return true;
	}


	// ERPNext adds "Switch to Frappe CRM" / "Switch to Helpdesk" promo banners (frappe.io links) to the sidebar.
	// Empty the list and make later pushes do nothing.
	function remove_sidebar_ads() {
		const list = window.frappe && frappe.ui && frappe.ui.sidebar_banners;
		if (!Array.isArray(list)) return false;
		list.length = 0;
		list.push = function () {
			return 0;
		};
		return true;
	}

	// Frappe never removes body.desktop-page when the SPA leaves the apps screen,
	// so we keep our own class in sync with the route and scope all apps-screen CSS to it.
	function sync_screen() {
		if (!document.body) return;
		let route = [];
		try {
			route = (window.frappe && frappe.get_route && frappe.get_route()) || [];
		} catch (e) {
			route = [];
		}
		const first = String(route[0] || "").toLowerCase();
		document.body.classList.toggle("b1-apps-screen", first === "" || first === "desktop");
	}

	function watch_routes() {
		if (!(window.frappe && frappe.router && frappe.router.on && document.body)) return false;
		if (frappe.router.__b1) return true;
		frappe.router.__b1 = true;
		frappe.router.on("change", sync_screen);
		sync_screen();
		return true;
	}

	function until(fn) {
		if (fn()) return;
		let tries = 0;
		const t = setInterval(() => {
			if (fn() || ++tries > 100) clearInterval(t);
		}, 50);
	}


	// ---- Dock avatar menu: add Support and About ----
	// The dock avatar and the sidebar user button both build their menu from frappe.ui.Sidebar.user_menu_options().
	function install_user_menu() {
		const S = window.frappe && frappe.ui && frappe.ui.Sidebar;
		if (!(S && S.prototype && S.prototype.user_menu_options)) return false;
		if (S.prototype.__b1_menu) return true;
		S.prototype.__b1_menu = true;
		const orig = S.prototype.user_menu_options;
		S.prototype.user_menu_options = function () {
			const groups = orig.apply(this, arguments);
			try {
				const first = groups && groups[0] && groups[0].options;
				if (Array.isArray(first)) {
					const at = first.findIndex((o) => o && o.name === "reload");
					first.splice(at < 0 ? first.length : at + 1, 0,
						{ name: "b1-support", label: __("Support"), icon: "life-buoy", onclick: () => frappe.ui.toolbar.b1_support() },
						{ name: "b1-about", label: __("About"), icon: "info", onclick: () => frappe.ui.toolbar.show_about() }
					);
				}
			} catch (e) {
				console.error("B-One user menu failed", e); // eslint-disable-line no-console
			}
			return groups;
		};
		return true;
	}

	// ---- Text scrubber: shows "B-One" instead of "ERPNext" / "Frappe" in interface text we cannot override at the source ----
	// Only touches text inside interface zones (dialogs, menus, sidebar, page head, field labels and help text).
	// Never touches inputs, code, lists, grids or editors, so user data stays as typed. Dotted names and URLs
	// (frappe.io, erpnext/templates, frappe.utils) are left alone. To switch it off, remove `until(install_scrubber)` below.
	const SCRUB_TEST = /(?<![\w./@\-])(erpnext|frappe)(?![\w./@\-])/i;
	const SCRUB_RE = /(?<![\w./@\-])(erpnext|frappe)(?![\w./@\-])/gi;
	const SCRUB_ZONES = ".modal, .dropdown-menu, .popover, .body-sidebar, .dock, .control-label, .help-box, .form-message, .section-head, .empty-state, .msgprint, .es-toast-container, .desktop-container, .sidebar-item-label";
	const SCRUB_SKIP = "input, textarea, select, option, pre, code, script, style, .ql-editor, .CodeMirror, .ace_editor, [contenteditable='true'], .list-row, .grid-static-col, .control-value, .awesomplete, [role='listbox'], .link-field";

	function scrub_text(n) {
		const v = n.nodeValue;
		if (!v || !SCRUB_TEST.test(v)) return;
		const el = n.parentElement;
		if (!el || el.closest(SCRUB_SKIP) || !el.closest(SCRUB_ZONES)) return;
		n.nodeValue = v.replace(SCRUB_RE, brand().name);
	}

	function scrub_tree(root) {
		if (!root) return;
		if (root.nodeType === 3) return scrub_text(root);
		if (root.nodeType !== 1) return;
		const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
		let n;
		while ((n = w.nextNode())) scrub_text(n);
	}

	function install_scrubber() {
		if (!document.body) return false;
		if (window.__b1_scrub) return true;
		window.__b1_scrub = true;
		const queued = new Set();
		let timer = null;
		const flush = () => {
			timer = null;
			const items = Array.from(queued);
			queued.clear();
			items.forEach(scrub_tree);
		};
		new MutationObserver((muts) => {
			muts.forEach((m) => {
				if (m.type === "characterData") queued.add(m.target);
				else m.addedNodes.forEach((x) => queued.add(x));
			});
			if (!timer) timer = setTimeout(flush, 30);
		}).observe(document.body, { childList: true, subtree: true, characterData: true });
		scrub_tree(document.body);
		return true;
	}

	until(install);
	until(watch_routes);
	until(install_brand_ui);
	until(remove_sidebar_ads);
	until(install_user_menu);
	until(install_scrubber);
})();