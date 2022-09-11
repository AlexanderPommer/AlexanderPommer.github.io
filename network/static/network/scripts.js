document.addEventListener('DOMContentLoaded', function() {

  // If user is logged in
  if (document.querySelector("#username-link")) {

    // Set action for clicking following link on navbar
    document.querySelector('#following-link').addEventListener('click', (event) => {
      // load following view
      load_view('following', 1);
      event.preventDefault();
      });

    // Set action for username link on navbar
    document.querySelector('#username-link').addEventListener('click', (event) => {
      load_profile(document.querySelector('#username-link strong').innerHTML);
      event.preventDefault();
    });
  }

    // By default, load all Posts
    load_view('all posts', 1);
  });


function create_post(event) {
  fetch('/create', {
    method: 'POST',
    body: JSON.stringify({
        body: document.querySelector('#post-body').value
      })
    })
  .then(response => {
    response.json();
    if (response.ok) {
      load_view('all posts', 1);
    }
  })
  document.querySelector('#post-body').value = '';
  event.preventDefault();
  }


function load_view(view, page) {

  // Pagination vars
  let prev_page = page - 1;
  let next_page = page + 1;

  // Clear pagination buttons
  try {
    document.querySelector('#prev-page').removeEventListener('click', prev_page_link);
  } catch {}
  try {
    document.querySelector('#next-page').removeEventListener('click', next_page_link);
  } catch {}

  // Clear previous posts and profile info if any
  try {
    document.querySelectorAll('div.post_div').forEach(div => {
      div.remove();
      });
    document.querySelectorAll('div.profile_div').forEach(div => {
      div.remove();
      });} catch (error) {}

  // Hide or Show sections depending on views
  if (view === 'all posts' || view == 'following') {

    // if user is logged in 
    if (document.querySelector("#username-link")) {

      // Display the new post form
      try {
        new_post_form = document.querySelector('#post-form');
        new_post_form.style.display = 'block';
        document.querySelector('#post-form').style.display = 'block';

        // Set the new post form's action
        new_post_form.addEventListener('submit', create_post);
      } catch {}
      
    }
    document.querySelector('#posts-view').style.display = 'block';
    }
  
  // Render view name
  document.querySelector('#posts-view').innerHTML = `<h2>${view}</h2>`;

  // Get posts data
  fetch(`/posts/${view}/${page}`)
  .then(response => response.json())
  .then(posts => {
    
    // User info variables
    let is_logged_in = false;
    let username = "";
    if (document.querySelector("#username-link")) {
      is_logged_in = true;
      username = document.querySelector('#username-link strong').innerHTML;
    }
    // Pagination variables
    let prev_page_exists = posts.slice(-2,-1)[0]["prev"];
    let next_page_exists = posts.slice(-1)[0]["next"];

      // Render at most 10 posts
      posts.slice(0,-2).forEach(post => {
        
        // Create and populate post with its contents
        const div = document.createElement('div');
        div.className = "post_div";
        div.id = `post${post.id}`;
        const poster = document.createElement('div');
        const link = document.createElement('a');
        poster.appendChild(link)
        link.innerHTML = `${post.poster}`;
        link.href = "";
        link.addEventListener('click', (event) => {
          load_profile(`${post.poster}`);
          event.preventDefault();
        })
        div.appendChild(poster);
        const body = document.createElement('div');
        body.innerHTML = `${post.body}`;
        body.className = "body";
        div.appendChild(body);
        const likes_row = document.createElement('div');
        likes_row.style.display = "flex";
        likes_row.className = "likes_row";
        const heart = document.createElement('div');
        heart.innerHTML = "&#x2764";
        heart.className = "heart";

        if (is_logged_in) {
          heart.addEventListener('click', () => like(post.id));
        }

        let likes = document.createElement('div');
        likes.innerHTML = `${post.likes}`;
        likes.className = "likes_num";

        likes_row.appendChild(heart);
        likes_row.appendChild(likes);
        div.appendChild(likes_row);
        const timestamp = document.createElement('div');
        timestamp.innerHTML =`${post.timestamp}`;
        div.appendChild(timestamp);

        // if user is logged in 
        if (is_logged_in) {

          // if user is post's author
          if (username === post.poster) {

            // Create edit button
            const edit_button = document.createElement('button');
            edit_button.className = "btn btn-sm btn-outline-secondary";
            edit_button.innerHTML = "edit";

            // Set edit_button action
            edit_button.addEventListener('click', (event) => {
              try {
                document.querySelectorAll('#post-form').forEach(form => form.removeEventListener('submit', submit_edit));
              } catch {}
              get_edit(post);
              event.preventDefault();
            });
            div.appendChild(edit_button);
          }
        }

      // Append post
        document.querySelector('#posts-view').appendChild(div);
      });
      
      // Set pagination links
      const prev_link = document.querySelector('#prev-page');
      if (prev_page_exists) {
        prev_link.parentElement.className = "page-item";
        prev_link.addEventListener('click', prev_page_link = (event) => {
          load_view(view, prev_page);
          event.preventDefault();
        }, { once: true });
      } else {
        prev_link.parentElement.className = "page-item disabled";
      }
      const next_link = document.querySelector('#next-page');
      if (next_page_exists) {
        next_link.parentElement.className = "page-item";
        
        next_link.addEventListener('click', next_page_link = (event) => {
          load_view(view, next_page);
          event.preventDefault();
        }, { once: true });
      } else {
        next_link.parentElement.className = "page-item disabled";
      }
  });
}


function load_profile(profile) {
  
  // Get profile data  
  fetch(`/profile/${profile}`)
    .then(response => response.json())
    .then(profile => {

      // Render the profile's posts
      load_view(`${profile[0].username}`, 1)

      // Hide new post form
      document.querySelector('#create-post-view').style.display = "none";

      // Render Follower/ing counts
      const div = document.createElement('div');
      div.className = "profile_div";
      div.innerHTML = `Followers: ${profile[0].followers}, Following: ${profile[0].following}`;
      document.querySelector('#posts-view').appendChild(div);

      // if user is logged in 
      if (document.querySelector("#username-link")) {

        // if user is not viewing own profile
        if (document.querySelector('#username-link strong').innerHTML !== document.querySelector('#posts-view h2').innerHTML) {

          // Create follow button
          const button = document.createElement('button');
          button.className = "btn btn-sm btn-outline-primary";

          // Add button text depending on follow status
          
          if (profile[0].followed === "True") {
            button.innerHTML = "Unfollow";
          } else {
            button.innerHTML = "Follow";
          }

          // Set follow button action
          button.addEventListener('click', follow);

          // Render button
          document.querySelector('#posts-view').appendChild(button);
        }
      }
    });
}


function follow(event) {
  username = document.querySelector('#posts-view h2').innerHTML;
  fetch('/follow', {
    method: 'PUT',
    body: JSON.stringify({
      username: username
      })
    })
  .then(response => {
    response.json();
    if (response.ok) {
      load_profile(username);
      }
    });
  event.preventDefault();
}


function get_edit(post) {

  let edit_form = document.querySelector('#post-form');
  let post_body = document.querySelector(`#post${post.id}`);
  let body = post_body.querySelector(".body");

  document.querySelectorAll(".body").forEach(body => body.style.display = "block");

  body.style.display = "none";
  document.querySelector(`#post${post.id} div`).append(edit_form);
  edit_form.style.display = "block"

  // Populate body field
  document.querySelector('#post-body').value = post.body;

  edit_form.removeEventListener('submit', create_post)
  edit_form.addEventListener('submit', submit_edit = (event) => {
    put_edit(post);
    event.preventDefault();
  }, { once: true });
}


function put_edit(post) {

  const new_body = document.querySelector('#post-body').value
  let post_body = document.querySelector(`#post${post.id}`);
  let body = post_body.querySelector(".body");

  fetch(`/edit/${post.id}`, {
    method: 'PUT',
    body: JSON.stringify({
        body: new_body
      })
    })
  .then(response => {
    if (response.ok) {

      let edit_form = document.querySelector('#post-form');
      body.innerHTML = new_body;
      edit_form.style.display = 'none';
      body.style.display = "block";

    }
  })
  // Clear form's body field
  document.querySelector('#post-body').value = '';
}


function like (post_id) {
  fetch(`/like`, {
    method: 'PUT',
    body: JSON.stringify({
      post_id: post_id
      })
    })
    .then(response => response.json())
    .then(post => {
      const post_div = document.querySelector(`#post${post_id}`);
      post_div.querySelector(".likes_num").innerHTML = post["likes"];
    })
}
