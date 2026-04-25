const buttons = document.querySelectorAll(".vote-btn");

buttons.forEach(btn => {
    btn.addEventListener("click", async () => {

        if (!confirm("Are you sure you want to vote?")) return;

        btn.disabled = true;

        const participantId = btn.getAttribute("data-id");

        try {
            const res = await fetch("/vote", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    participant_id: participantId
                })
            });

            const data = await res.json();

            if (data.status === "success") {

                showToast("Vote submitted successfully.")

                buttons.forEach(b => {
                    b.classList.remove("bg-green-500", "text-white");
                    b.classList.add("bg-gray-300", "cursor-not-allowed");
                    b.disabled = true;
                });

                btn.classList.remove("bg-gray-300", "cursor-not-allowed");
                btn.classList.add("bg-green-500", "text-white");
                btn.disabled = true;

            } else {
                showToast(data.message);
                btn.disabled = false;
            }

        } catch (error) {
            showToast("Something went wrong. Try again.");
            btn.disabled = false;
            console.error(error);
        }
    });
});

function showToast(message) {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.classList.remove("hidden");

    setTimeout(() => {
        toast.classList.add("hidden");
    }, 3000);
}