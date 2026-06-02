"""Blueprint del portal institucional."""

from flask import Blueprint, redirect, render_template, request, url_for

from data.portal_data import (
    LINKS_UTILES,
    get_portal_area,
    get_portal_cards,
    normalize_area_slug,
)
from services.data_service import format_date, get_centro, get_current_user, get_notices

portal_bp = Blueprint("portal", __name__)


def _build_context(area_slug=None):
    avisos = get_notices()
    for aviso in avisos:
        aviso["_fecha"] = format_date(aviso["fecha"])

    return {
        "usuario": get_current_user(),
        "centro": get_centro(),
        "portal_cards": get_portal_cards(),
        "links_utiles": LINKS_UTILES,
        "avisos": avisos,
        "area_activa": get_portal_area(area_slug) if area_slug else None,
        "active_area_slug": area_slug,
    }


@portal_bp.route("/portal")
def portal():
    area = request.args.get("area")
    if area:
        return redirect(url_for("portal.portal_area", area_slug=normalize_area_slug(area)))

    return render_template("portal.html", **_build_context())


@portal_bp.route("/portal/<area_slug>")
def portal_area(area_slug):
    area_slug = normalize_area_slug(area_slug)
    if not get_portal_area(area_slug):
        return render_template("404.html", usuario=get_current_user()), 404

    return render_template("portal.html", **_build_context(area_slug))
