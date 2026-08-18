from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / 'figures'

NAVY = '#173F6B'
TEXT = '#13253A'
LINE = '#27445F'
ACTOR = '#EAF3FB'
GATEWAY = '#DCECF8'
TRUST = '#E8F5DF'
TRUST_EDGE = '#6A9E4B'
EDU = '#FFF1D6'
EDU_EDGE = '#D99529'
DATA = '#F9E3EA'
DATA_EDGE = '#C95A72'
ACCOUNT = '#EEE8F8'
ACCOUNT_EDGE = '#6A56A1'
OUTCOME = '#EEF6FF'
OUTCOME_EDGE = '#5A8FC1'
WHITE = '#FFFFFF'


def add_box(ax, x, y, w, h, text, face, edge=LINE, fontsize=8.0, weight='semibold', radius=0.018, lw=1.15, z=2, color=TEXT):
    box = FancyBboxPatch((x, y), w, h,
                         boxstyle=f'round,pad=0.006,rounding_size={radius}',
                         facecolor=face, edgecolor=edge, linewidth=lw,
                         mutation_aspect=1, zorder=z)
    ax.add_patch(box)
    ax.text(x+w/2, y+h/2, text, ha='center', va='center',
            fontsize=fontsize, fontweight=weight, color=color,
            linespacing=1.12, zorder=z+1)
    return box


def add_arrow(ax, x1, y1, x2, y2, color=LINE, lw=1.05, style='-|>', ms=11, z=4, connection='arc3'):
    arr = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                          mutation_scale=ms, linewidth=lw, color=color,
                          connectionstyle=connection, shrinkA=0, shrinkB=0,
                          zorder=z)
    ax.add_patch(arr)
    return arr


def step_badge(ax, x, y, num):
    c = Circle((x, y), 0.013, facecolor=NAVY, edgecolor='white', linewidth=1.1, zorder=6)
    ax.add_patch(c)
    ax.text(x, y, str(num), ha='center', va='center', color='white', fontsize=7.2, fontweight='bold', zorder=7)


def main():
    plt.rcParams.update({
        'font.family': 'DejaVu Sans',
        'pdf.fonttype': 42,
        'ps.fonttype': 42,
    })
    fig, ax = plt.subplots(figsize=(8.2, 5.25))
    fig.patch.set_facecolor('white')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Title and subtitle
    ax.text(0.02, 0.972, 'AFRICA-ZT-EDU reference architecture',
            ha='left', va='top', fontsize=13.4, fontweight='bold', color=NAVY)
    ax.text(0.02, 0.933, 'Policy-governed, Zero-Trust, privacy-preserving and jurisdiction-aware decision path',
            ha='left', va='top', fontsize=8.4, color='#496078')
    ax.plot([0.02, 0.98], [0.910, 0.910], color='#9CB4C9', linewidth=0.8)

    # Actor cards
    actor_y, actor_h = 0.805, 0.075
    actor_w = 0.205
    actor_xs = [0.085, 0.325, 0.565]
    actor_texts = [
        'Learners & staff\nPasskey + device posture',
        'Institutions\nIssuer + relying party',
        'Partners & regulators\nControlled verification',
    ]
    for i, (x, text) in enumerate(zip(actor_xs, actor_texts), start=1):
        add_box(ax, x, actor_y, actor_w, actor_h, text, ACTOR, edge=NAVY, fontsize=8.0, radius=0.016)

    # Gateway
    add_box(ax, 0.085, 0.710, 0.685, 0.065,
            'Regional access and transfer gateways - North | West | East | Central | Southern Africa\nPEP + API gateway + mTLS + rate limits + low-bandwidth synchronization',
            GATEWAY, edge=NAVY, fontsize=7.7, radius=0.015, lw=1.2)

    # Outcome panel
    add_box(ax, 0.805, 0.218, 0.175, 0.662, '', WHITE, edge='#9CB4C9', fontsize=8, radius=0.014, lw=1.05)
    ax.text(0.8925, 0.858, 'Governed outcomes', ha='center', va='center', fontsize=8.8, fontweight='bold', color=NAVY)
    outcome_items = [
        ('Secure access', 0.755),
        ('Privacy protection', 0.650),
        ('Controlled transfers', 0.545),
        ('Minimal disclosure', 0.440),
        ('Auditable resilience', 0.335),
    ]
    for label, yy in outcome_items:
        add_box(ax, 0.822, yy, 0.141, 0.072, label, OUTCOME, edge=OUTCOME_EDGE, fontsize=7.4, radius=0.012, weight='semibold', lw=0.9)
    ax.text(0.8925, 0.245, 'Short-lived claim views\n+ signed decision receipts', ha='center', va='center', fontsize=7.0, color='#496078', linespacing=1.2)

    # Layer labels and nodes
    label_x, label_w = 0.020, 0.105
    node_xs = [0.145, 0.310, 0.475, 0.640]
    node_w = 0.145

    # Trust & policy row
    y1, h1 = 0.535, 0.125
    add_box(ax, label_x, y1, label_w, h1, 'TRUST &\nPOLICY', TRUST, edge=TRUST_EDGE, fontsize=8.2, radius=0.015, lw=1.1)
    trust_texts = [
        'Identity\nFIDO2 + OIDC\nWorkload ID',
        'PDP / policy engine\nSubject + device\nPurpose + risk',
        'Jurisdiction profile\nBasis + safeguards\nFields + retention',
        'Consent + rights\nObligations\nReceipts',
    ]
    for x, text in zip(node_xs, trust_texts):
        add_box(ax, x, y1, node_w, h1, text, TRUST, edge=TRUST_EDGE, fontsize=7.7, radius=0.014, lw=1.0)

    # Education row
    y2, h2 = 0.350, 0.125
    add_box(ax, label_x, y2, label_w, h2, 'EDUCATION\nSERVICES', EDU, edge=EDU_EDGE, fontsize=8.0, radius=0.015, lw=1.1)
    edu_texts = [
        'LMS\nContent delivery\nEvent stream',
        'SIS / assessment\nGrades\nProctoring bounds',
        'Credential issuer\nW3C VC 2.0\nStatus list',
        'Wallet / verifier\nSelective claims\nOffline freshness',
    ]
    for x, text in zip(node_xs, edu_texts):
        add_box(ax, x, y2, node_w, h2, text, EDU, edge=EDU_EDGE, fontsize=7.7, radius=0.014, lw=1.0)

    # Data & privacy row
    y3, h3 = 0.170, 0.125
    add_box(ax, label_x, y3, label_w, h3, 'DATA &\nPRIVACY', DATA, edge=DATA_EDGE, fontsize=8.2, radius=0.015, lw=1.1)
    data_xs = [0.145, 0.365, 0.585]
    data_ws = [0.200, 0.200, 0.200]
    data_texts = [
        'Regional vaults\nClassification + encryption\nTokenization + KMS/HSM',
        'Minimized claim views\nPurpose + fields + expiry\nReceipts + deletion hooks',
        'Private analytics\nPseudonymization\nAggregation + budgets\nFederation',
    ]
    for x, w, text in zip(data_xs, data_ws, data_texts):
        add_box(ax, x, y3, w, h3, text, DATA, edge=DATA_EDGE, fontsize=7.5, radius=0.014, lw=1.0)

    # Accountability row
    y4, h4 = 0.035, 0.090
    add_box(ax, label_x, y4, label_w, h4, 'ACCOUNTABILITY\n& RESILIENCE', ACCOUNT, edge=ACCOUNT_EDGE, fontsize=6.3, radius=0.015, lw=1.1)
    add_box(ax, 0.145, y4, 0.640, h4,
            'Signed receipts + append-only audit + SIEM/DLP\nIncident workflow + policy versions + asynchronous buffering',
            ACCOUNT, edge=ACCOUNT_EDGE, fontsize=7.5, radius=0.014, lw=1.0)

    # Arrows kept entirely in inter-row whitespace.
    actor_centers = [x + actor_w/2 for x in actor_xs]
    for x in actor_centers:
        add_arrow(ax, x, actor_y, x, 0.775, lw=1.0)

    trust_centers = [x + node_w/2 for x in node_xs]
    for x in trust_centers:
        add_arrow(ax, x, 0.710, x, y1+h1, lw=1.0)

    edu_centers = [x + node_w/2 for x in node_xs]
    for x in edu_centers:
        add_arrow(ax, x, y1, x, y2+h2, lw=1.0)

    # Education -> data, routed only through the gap.
    add_arrow(ax, edu_centers[0], y2, data_xs[0]+data_ws[0]/2, y3+h3, lw=1.0)
    add_arrow(ax, edu_centers[1], y2, data_xs[1]+data_ws[1]/2, y3+h3, lw=1.0)
    add_arrow(ax, edu_centers[2], y2, data_xs[1]+data_ws[1]/2, y3+h3, lw=1.0)
    add_arrow(ax, edu_centers[3], y2, data_xs[2]+data_ws[2]/2, y3+h3, lw=1.0)

    # Data -> accountability
    for x, w in zip(data_xs, data_ws):
        add_arrow(ax, x+w/2, y3, x+w/2, y4+h4, lw=1.0)

    # Gateway and control evidence to outcomes; route around panel boundary.
    add_arrow(ax, 0.770, 0.742, 0.805, 0.742, color=OUTCOME_EDGE, lw=1.0)

    # Compact legend/footer inside figure.
    ax.text(0.805, 0.178, 'Solid arrows: data/control flow', ha='left', va='center', fontsize=6.6, color='#496078')
    ax.text(0.805, 0.150, 'All releases are policy-scoped', ha='left', va='center', fontsize=6.6, color='#496078')

    fig.subplots_adjust(left=0.015, right=0.995, top=0.995, bottom=0.015)
    out_png = FIG / 'reference_architecture_v3.png'
    out_pdf = FIG / 'reference_architecture_v3.pdf'
    fig.savefig(out_png, dpi=360, bbox_inches='tight', pad_inches=0.03, facecolor='white')
    fig.savefig(out_pdf, bbox_inches='tight', pad_inches=0.03, facecolor='white')
    plt.close(fig)
    print(out_png)
    print(out_pdf)

if __name__ == '__main__':
    main()
