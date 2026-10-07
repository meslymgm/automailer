from models import DailyBriefing
def render_briefing_html(
        briefing: DailyBriefing
)->str:
    html = f"""
<html>
<body>
    <h1>{briefing.headline}</h1>
"""
    for item in briefing.items:
        html += f"""
        <h2>{item.category.value}</h2>
        <h3>{item.title}</h3>
        <p>{item.summary}</p>
        <p><strong>Why it matters:</strong> {item.why_it_matters}</p>
        <p><a href="{item.source}">Read source</a></p>
        <hr>
        """

    html += f"""
    <p><strong>Closing thought:</strong> {briefing.closing_thought}</p>
    </body>
    </html>
    """

    return html
