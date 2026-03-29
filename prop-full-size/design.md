# Design.md

## 1\. Theme

* **Mode:** Light Theme
* **Primary colors:**
  * `#FFFFFF`
  * `#F6F6F6`
  * `#DFDFDF`
* **Accent color:**

  * `#3B82F6`

\---

## 2\. Global Layout Rules

### 2.1 Content Inset

Except for **full-bleed background images**, all page content should keep a fixed distance from **both** the left and right edges.

* **Global horizontal inset:** `32px` (left **and** right)
* Applies to:

  * image frames
  * titles
  * text blocks
  * cards
  * content containers

### 2.2 Section Title Position

Each section's **secondary title** should:

* be **left-aligned**
* keep the same fixed distance from the left edge as the global inset
* keep the same fixed distance from the top edge of the section
* **Left offset:** `32px`
* **Top offset:** `32px`

\---

## 3\. Corner Radius

* **Global radius:** `0.25rem`

Applies to:

* image frames
* cards
* buttons
* panels
* containers

\---

## 4\. Typography

* **Font family:** `Inter`

Use only these 5 fixed text sizes:

### 4.1 Hero Title

Used for:

* main title on HERO section
* **Size:** `72px`
* **Font weight:** `400`
* **Line height:** `1`
* **Letter spacing:** `tracking-tighter` (`-0.05em`)

### 4.2 Secondary Title

Used for:

* the intro title at the beginning of each screen / section
* **Size:** `36px`
* **Font weight:** `400`
* **Line height:** `1`
* **Letter spacing:** `tracking-tighter` (`-0.05em`)

### 4.3 Tertiary Title

Used for:

* small titles inside frames / cards / modules
* **Size:** `20px`
* **Font weight:** `400`
* **Line height:** `1`
* **Letter spacing:** `tracking-tighter` (`-0.05em`)

### 4.4 Body Text

Used for:

* standard paragraph text
* descriptive copy
* **Size:** `15px`
* **Font weight:** `400`
* **Line height:** `1`
* **Letter spacing:** `tracking-tighter` (`-0.05em`)

### 4.5 Small Text

Used for:

* captions
* labels
* notes
* helper text
* **Size:** `12px`
* **Font weight:** `400`
* **Line height:** `1`
* **Letter spacing:** `tracking-tighter` (`-0.05em`)

\---

## 5\. Icons

* **Arrow icon:** Material Symbols `arrow_outward`
* **Arrow size:** `20px`

\---

## 6\. Usage Rule

When a title type is mentioned later, always use the fixed size defined above:

* **HERO title** → `72px`
* **Secondary title** → `36px`
* **Tertiary title** → `20px`
* **Body text** → `15px`
* **Small text** → `12px`

\---

## 7\. Summary

This design system should follow:

* light theme
* Inter only
* fixed horizontal inset: `32px` (left **and** right)
* section secondary title aligned left with `32px` left / top offset
* global corner radius: `0.25rem`
* 5 fixed font sizes only
* arrow icon size: `20px`

