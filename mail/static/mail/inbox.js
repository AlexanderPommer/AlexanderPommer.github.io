document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);
  // Send Email
  document.querySelector('#compose-form').addEventListener('submit', send_email);

  // By default, load the inbox
  load_mailbox('inbox');
});

function send_email(event) {
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
        recipients: document.querySelector('#compose-recipients').value,
        subject: document.querySelector('#compose-subject').value,
        body: document.querySelector('#compose-body').value
      })
    })
  .then(response => {
    response.json();
    if (response.ok) {
      load_mailbox('sent');
    }
  })
  event.preventDefault();
  }

function compose_email() {

  // Clear previous email divs
  document.querySelectorAll('div.email_div').forEach(div => {
    div.remove();
  });

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {

  // Clear previous email divs
  document.querySelectorAll('div.email_div').forEach(div => {
    div.remove();
  });
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // GET /emails/<mailbox>
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
      // console.log(emails);

      // Make Div and render email contents
      emails.forEach(email => {
        const div = document.createElement('div');
        div.className = "email_div";
        div.id = `${email.id}`;
        const sender = document.createElement('p');
        sender.innerHTML = `From: ${email.sender}`;
        div.appendChild(sender);
        const subject = document.createElement('p');
        subject.innerHTML = `Subject: ${email.subject}`;
        div.appendChild(subject);
        const timestamp = document.createElement('p');
        timestamp.innerHTML =`Timestamp: ${email.timestamp}`;
        div.appendChild(timestamp);
        if (email.read) {
          div.style.background = "gray";
        }
        else {
          div.style.background = "white";
        }
        div.addEventListener('click', () => view_email(`${email.id}`));
        // Populate email contents
        document.querySelector('#emails-view').appendChild(div);
      });
  });
}

function view_email(email_id) {
  // Clear previous email divs
  document.querySelectorAll('div.email_div').forEach(div => {
    div.remove();
  });

  fetch(`/emails/${email_id}`)
  .then(response => response.json())
  .then(email => {
      // console.log(email);

      // Create email Div
      const div = document.createElement('div');
      div.className = "email_div"
      const sender = document.createElement('div');
      sender.innerHTML= `Sender: ${email.sender}`;
      div.appendChild(sender);
      const recipients = document.createElement('ul');
      recipients.innerHTML = "Recipients:"
      email.recipients.forEach(recipient => {
        const recip = document.createElement('li');
        recip.innerHTML = recipient
        recipients.append(recip)
      })
      div.appendChild(recipients)
      const subject = document.createElement('div');
      subject.innerHTML = `Subject : ${email.subject}`;
      div.appendChild(subject);
      const timestamp = document.createElement('div');
      timestamp.innerHTML = `Timestamp: ${email.timestamp}`;
      div.appendChild(timestamp);
      const body_ = document.createElement('div');
      body_.innerHTML = ` Body: ${email.body}`;
      div.appendChild(body_);
      div.style.display = 'block';

      // Archive button logic
      if (email.sender != document.querySelector('h2').innerHTML) {
        const toarchive = document.createElement('button');
        if (email.archived) {
          toarchive.addEventListener('click', () => unarchive(`${email.id}`));
          toarchive.innerHTML = "Unarchive";
        }
        else {
          toarchive.addEventListener('click', () => archive(`${email.id}`));
          toarchive.innerHTML = "Archive";
        }
        toarchive.className ="btn btn-sm btn-outline-secondary"
        div.appendChild(toarchive);
      }

      // Reply button logic
      const em = email;
      const reply_button = document.createElement('button');
      reply_button.addEventListener('click', () => reply(email));
      reply_button.innerHTML = 'Reply';
      div.appendChild(reply_button);
      reply_button.className ="btn btn-sm btn-outline-secondary";
      document.querySelector('.container').appendChild(div);

      // Hide other sections
      document.querySelector('#emails-view').style.display = 'none';
      document.querySelector('#compose-view').style.display = 'none';

  });
  // Mark email as viewed
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
        read: true
    })
  })
}

function archive(email_id) {
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
      archived: true
    })
  }).then(() => load_mailbox('inbox'))
}
function unarchive(email_id) {
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
      archived: false
    })
  }).then(() => load_mailbox('inbox'))
}

function reply(email) {

  // Clear previous email divs
  document.querySelectorAll('div.email_div').forEach(div => {
    div.remove();
  });

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Pre-fill composition fields
  document.querySelector('#compose-recipients').value = email.sender;
  if (email.subject.slice(0,4) === `Re: `) {
    document.querySelector('#compose-subject').value = email.subject; 
  }
  else {
    document.querySelector('#compose-subject').value = `Re: ${email.subject}`;
  }
  document.querySelector('#compose-body').value = `On ${email.timestamp} ${email.sender} wrote: ${email.body}`;
}
