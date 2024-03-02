export default function Page() {
  return <div className="container">
			<div className="email-list">
				{% for email in email_list %}
                <div class="email-list-item">{{ email }}</div>
            	{% endfor %}
			</div>
			<div className="email-viewer">
				<h2>Email Viewer</h2>
				<p>Click on an email to view its content.</p>
			</div>
		</div>
}