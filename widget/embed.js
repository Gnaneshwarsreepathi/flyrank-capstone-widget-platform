(function () {
  "use strict";

  const script =
    document.currentScript ||
    document.querySelector("script[data-widget-id]");

  if (!script) {
    console.error("FlyRank Widget: script tag not found.");
    return;
  }

  const widgetId = script.getAttribute("data-widget-id");
  const apiBase =
    script.getAttribute("data-api-base") || "http://127.0.0.1:8000";

  if (!widgetId) {
    console.error("FlyRank Widget: data-widget-id is required.");
    return;
  }

  async function loadWidget() {
    try {
      const response = await fetch(
        `${apiBase}/widgets/${widgetId}/config`
      );

      if (!response.ok) {
        throw new Error(`Widget config request failed: ${response.status}`);
      }

      const config = await response.json();
      renderWidget(config);
    } catch (error) {
      console.error("FlyRank Widget:", error);
    }
  }

  function renderWidget(config) {
    const container = document.createElement("div");

    container.id = `flyrank-widget-${widgetId}`;

    container.style.maxWidth = "420px";
    container.style.margin = "20px auto";
    container.style.padding = "24px";
    container.style.border = "1px solid #ddd";
    container.style.borderRadius = "12px";
    container.style.background = "#fff";
    container.style.fontFamily =
      "Arial, sans-serif";
    container.style.boxShadow =
      "0 4px 12px rgba(0, 0, 0, 0.08)";

    const title = document.createElement("h2");
    title.textContent = config.title || "Contact Us";
    title.style.marginTop = "0";

    container.appendChild(title);

    if (config.description) {
      const description = document.createElement("p");
      description.textContent = config.description;
      container.appendChild(description);
    }

    const form = document.createElement("form");

    const fields = config.form_fields || {};

    Object.entries(fields).forEach(([fieldName, fieldConfig]) => {
      const wrapper = document.createElement("div");
      wrapper.style.marginBottom = "14px";

      const label = document.createElement("label");
      label.textContent =
        fieldConfig.label || fieldName;
      label.style.display = "block";
      label.style.marginBottom = "6px";

      const input = document.createElement("input");

      input.name = fieldName;
      input.type = fieldConfig.type || "text";
      input.required = Boolean(fieldConfig.required);

      input.style.width = "100%";
      input.style.boxSizing = "border-box";
      input.style.padding = "10px";
      input.style.border = "1px solid #ccc";
      input.style.borderRadius = "6px";

      wrapper.appendChild(label);
      wrapper.appendChild(input);
      form.appendChild(wrapper);
    });

    const submitButton = document.createElement("button");

    submitButton.type = "submit";
    submitButton.textContent =
      config.button_text || "Submit";

    submitButton.style.padding = "10px 18px";
    submitButton.style.border = "none";
    submitButton.style.borderRadius = "6px";
    submitButton.style.cursor = "pointer";

    form.appendChild(submitButton);

    const message = document.createElement("p");

    message.style.marginTop = "14px";

    form.addEventListener("submit", async function (event) {
      event.preventDefault();

      submitButton.disabled = true;
      message.textContent = "Submitting...";

      const formData = new FormData(form);
      const payload = {};

      formData.forEach((value, key) => {
        payload[key] = value;
      });

      try {
        const response = await fetch(
          `${apiBase}/submissions`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "Idempotency-Key":
                crypto.randomUUID(),
            },
            body: JSON.stringify({
              widget_id: Number(widgetId),
              payload: payload,
            }),
          }
        );

        if (!response.ok) {
          throw new Error(
            `Submission failed: ${response.status}`
          );
        }

        message.textContent =
          "Thank you! Your submission was received.";

        form.reset();
      } catch (error) {
        console.error(
          "FlyRank Widget submission error:",
          error
        );

        message.textContent =
          "Something went wrong. Please try again.";
      } finally {
        submitButton.disabled = false;
      }
    });

    container.appendChild(form);
    container.appendChild(message);

    script.parentNode.insertBefore(
      container,
      script.nextSibling
    );
  }

  loadWidget();
})();