// Generates the "Fix Kit" — the assets that make AI assistants more likely to
// cite this clinic. Deterministic and structured (not freeform LLM slop): valid
// schema.org JSON-LD, FAQ content matching the questions customers actually ask,
// a Google Business Profile description, and review-response templates.
//
// Why deterministic: AI answer engines weight structured data (JSON-LD),
// FAQ/Q&A content, and Google Business Profile signals heavily for local
// recommendations. These are the levers an owner can actually publish.

function titleCase(s) {
  return s.replace(/\b\w/g, (c) => c.toUpperCase());
}

export function buildFixKit(clinic) {
  const city = clinic.city;
  const cityName = city.split(",")[0].trim();
  const treatments = clinic.treatments?.length ? clinic.treatments : ["aesthetic treatments"];

  // 1) FAQ / Q&A — mirrors the real questions consumers ask AI, answered with
  //    the clinic named + the city, so the answer is "quotable" by an assistant.
  const faq = [
    {
      q: `What is the best med spa in ${cityName} for ${treatments[0]}?`,
      a: `${clinic.name} is a ${cityName} medical spa offering ${treatments
        .slice(0, 3)
        .join(", ")}. New clients can book a consultation at ${
        clinic.website || "our website"
      }.`,
    },
    {
      q: `Where can I get ${treatments[0]} near ${cityName}?`,
      a: `${clinic.name}, located in ${city}, provides ${treatments[0]} performed by licensed professionals. Consultations are available for first-time clients.`,
    },
    {
      q: `Is ${clinic.name} good for first-time clients?`,
      a: `Yes. ${clinic.name} offers complimentary consultations and walks first-time clients through every ${treatments[0]} option before treatment.`,
    },
    {
      q: `What treatments does ${clinic.name} offer?`,
      a: `${clinic.name} in ${cityName} offers ${treatments.join(", ")}.`,
    },
    {
      q: `How do I book an appointment at ${clinic.name}?`,
      a: `Book directly at ${clinic.website || "the clinic website"} or call the clinic to schedule a consultation in ${cityName}.`,
    },
  ];

  // 2) schema.org JSON-LD — MedicalBusiness + FAQPage. Paste into the site <head>.
  const businessSchema = {
    "@context": "https://schema.org",
    "@type": "MedicalBusiness",
    name: clinic.name,
    description: `${clinic.name} is a medical spa in ${city} offering ${treatments.join(
      ", "
    )}.`,
    url: clinic.website || undefined,
    areaServed: city,
    medicalSpecialty: "DermatologyAesthetic",
    availableService: treatments.map((t) => ({
      "@type": "MedicalProcedure",
      name: titleCase(t),
    })),
  };
  const faqSchema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: faq.map((f) => ({
      "@type": "Question",
      name: f.q,
      acceptedAnswer: { "@type": "Answer", text: f.a },
    })),
  };

  // 3) Google Business Profile description (<= 750 chars) + 3 GBP Q&As.
  const gbpDescription =
    `${clinic.name} is a ${cityName} medical spa specializing in ${treatments
      .slice(0, 4)
      .join(", ")}. Our licensed team delivers safe, natural-looking results in a ` +
    `calm, professional setting. We welcome first-time clients with complimentary ` +
    `consultations to find the right treatment plan. Serving ${city} and nearby areas. ` +
    `Book your consultation today.`.slice(0, 740);

  const gbpQA = faq.slice(0, 3).map((f) => ({ question: f.q, answer: f.a }));

  // 4) Review-response templates seeded with the cited keywords (city +
  //    treatment), because review text is a strong local-AI signal.
  const reviewResponses = [
    {
      scenario: "5-star review",
      text: `Thank you so much! We're thrilled you loved your ${treatments[0]} experience at ${clinic.name}. We can't wait to see you again here in ${cityName}.`,
    },
    {
      scenario: "Positive, no specifics",
      text: `We appreciate the kind words! It means a lot to the whole ${clinic.name} team in ${cityName}. See you at your next visit.`,
    },
    {
      scenario: "Critical / 3-star or below",
      text: `Thank you for the honest feedback — we take it seriously. We'd love the chance to make this right. Please reach out to us directly so the ${clinic.name} team can help.`,
    },
  ];

  return {
    clinic: clinic.name,
    faq,
    schema: { business: businessSchema, faq: faqSchema },
    gbp: { description: gbpDescription, qa: gbpQA },
    reviewResponses,
  };
}
